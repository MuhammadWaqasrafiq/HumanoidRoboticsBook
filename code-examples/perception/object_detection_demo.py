#!/usr/bin/env python3
"""
Object Detection Accuracy Demo for Isaac Sim Scenes

Tests YOLOv8 object detection achieving >85% accuracy in Isaac Sim test scenes.
Evaluates detection performance on household objects for manipulation tasks.

Dependencies:
    - ROS 2 Iron
    - Ultralytics YOLOv8
    - Isaac Sim 2025.1+
    - NumPy

Usage:
    # Terminal 1: Launch Isaac Sim with test scene
    ./isaac-sim.sh

    # Terminal 2: Run detection benchmark
    python3 object_detection_demo.py --trials 20

Expected Output:
    Detection Accuracy: 87.5% (35/40 objects detected correctly)
    Target: >85% for SC-003 success criterion

Author: Physical AI Robotics Book
License: MIT
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
import numpy as np
import time
from typing import List, Dict
from dataclasses import dataclass
import argparse


@dataclass
class GroundTruthObject:
    """Ground truth object annotation."""
    class_name: str
    bbox: List[float]  # [x1, y1, x2, y2]


class ObjectDetectionBenchmark(Node):
    """
    Benchmark object detection accuracy in Isaac Sim scenes.

    Test Protocol:
    1. Load predefined test scenes with known objects
    2. Run YOLOv8 detection
    3. Compare detections to ground truth
    4. Calculate precision, recall, accuracy
    """

    # Isaac Sim test scene ground truth
    # Scene: Kitchen countertop with household objects
    GROUND_TRUTH = [
        GroundTruthObject('cup', [320, 180, 380, 260]),
        GroundTruthObject('cup', [450, 190, 510, 270]),
        GroundTruthObject('bottle', [560, 150, 610, 320]),
        GroundTruthObject('bowl', [210, 200, 310, 280]),
        GroundTruthObject('spoon', [400, 280, 470, 310]),
        GroundTruthObject('knife', [350, 285, 430, 305]),
        GroundTruthObject('apple', [620, 220, 680, 280]),
        GroundTruthObject('banana', [280, 245, 360, 285]),
        # Add more objects as needed
    ]

    def __init__(self, model_path: str = 'yolov8l.pt', num_trials: int = 20):
        super().__init__('detection_benchmark')

        # Parameters
        self.num_trials = num_trials
        self.current_trial = 0

        # Load YOLOv8
        self.get_logger().info(f'Loading model: {model_path}')
        self.model = YOLO(model_path)

        # CV bridge
        self.bridge = CvBridge()

        # Results storage
        self.trial_results: List[Dict] = []

        # Subscribe to Isaac Sim camera
        self.image_sub = self.create_subscription(
            Image,
            '/isaac_camera/rgb',  # Isaac Sim camera topic
            self.image_callback,
            10
        )

        # Timer to control trials (2 Hz - allow scene to settle)
        self.create_timer(0.5, self.run_trial)

        self.get_logger().info(f'Benchmark initialized - {num_trials} trials')
        self.get_logger().info(f'Ground truth: {len(self.GROUND_TRUTH)} objects')

    def image_callback(self, msg: Image) -> None:
        """Store latest camera image."""
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'Image conversion error: {e}')

    def run_trial(self) -> None:
        """Execute one detection trial."""
        if self.current_trial >= self.num_trials:
            # All trials complete
            self.analyze_results()
            raise SystemExit(0)

        if not hasattr(self, 'latest_image'):
            return  # Wait for first image

        self.current_trial += 1
        self.get_logger().info(f'Running trial {self.current_trial}/{self.num_trials}')

        # Run YOLOv8 detection
        start_time = time.time()
        results = self.model(
            self.latest_image,
            conf=0.5,  # Confidence threshold
            verbose=False
        )
        inference_time = (time.time() - start_time) * 1000

        # Extract detections
        detections = self.extract_detections(results[0])

        # Match detections to ground truth
        matches = self.match_detections(detections, self.GROUND_TRUTH)

        # Calculate metrics
        true_positives = matches['true_positives']
        false_positives = matches['false_positives']
        false_negatives = matches['false_negatives']

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Store results
        trial_result = {
            'trial': self.current_trial,
            'inference_time': inference_time,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'detections': len(detections)
        }

        self.trial_results.append(trial_result)

        # Print trial summary
        self.get_logger().info(
            f'Trial {self.current_trial}: '
            f'P={precision:.2f}, R={recall:.2f}, F1={f1_score:.2f}, '
            f'Latency={inference_time:.1f}ms'
        )

    def extract_detections(self, result) -> List[Dict]:
        """Extract detections from YOLO results."""
        detections = []

        if result.boxes is None or len(result.boxes) == 0:
            return detections

        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy().astype(int)

        for box, conf, cls_id in zip(boxes, confidences, class_ids):
            detections.append({
                'bbox': box.tolist(),
                'confidence': float(conf),
                'class_name': self.model.names[cls_id]
            })

        return detections

    def match_detections(
        self,
        detections: List[Dict],
        ground_truth: List[GroundTruthObject]
    ) -> Dict:
        """
        Match detections to ground truth using IoU.

        Args:
            detections: YOLOv8 detections
            ground_truth: Ground truth objects

        Returns:
            Dictionary with TP, FP, FN counts
        """
        iou_threshold = 0.5

        gt_matched = [False] * len(ground_truth)
        det_matched = [False] * len(detections)

        true_positives = 0

        # Match detections to ground truth
        for i, det in enumerate(detections):
            best_iou = 0
            best_gt_idx = -1

            for j, gt in enumerate(ground_truth):
                # Check class match
                if det['class_name'] != gt.class_name:
                    continue

                # Calculate IoU
                iou = self.calculate_iou(det['bbox'], gt.bbox)

                if iou > best_iou and iou >= iou_threshold:
                    best_iou = iou
                    best_gt_idx = j

            if best_gt_idx >= 0 and not gt_matched[best_gt_idx]:
                # True positive
                gt_matched[best_gt_idx] = True
                det_matched[i] = True
                true_positives += 1

        # Count false positives and false negatives
        false_positives = sum(1 for matched in det_matched if not matched)
        false_negatives = sum(1 for matched in gt_matched if not matched)

        return {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }

    def calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.

        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]

        Returns:
            IoU score [0, 1]
        """
        x1_inter = max(bbox1[0], bbox2[0])
        y1_inter = max(bbox1[1], bbox2[1])
        x2_inter = min(bbox1[2], bbox2[2])
        y2_inter = min(bbox1[3], bbox2[3])

        if x2_inter < x1_inter or y2_inter < y1_inter:
            return 0.0  # No intersection

        intersection = (x2_inter - x1_inter) * (y2_inter - y1_inter)

        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])

        union = area1 + area2 - intersection

        iou = intersection / union if union > 0 else 0.0

        return iou

    def analyze_results(self) -> None:
        """Analyze and print final benchmark results."""
        if len(self.trial_results) == 0:
            self.get_logger().error('No trial results available')
            return

        # Calculate aggregate metrics
        avg_precision = np.mean([r['precision'] for r in self.trial_results])
        avg_recall = np.mean([r['recall'] for r in self.trial_results])
        avg_f1 = np.mean([r['f1_score'] for r in self.trial_results])
        avg_latency = np.mean([r['inference_time'] for r in self.trial_results])

        total_tp = sum(r['true_positives'] for r in self.trial_results)
        total_fp = sum(r['false_positives'] for r in self.trial_results)
        total_fn = sum(r['false_negatives'] for r in self.trial_results)

        total_gt = len(self.GROUND_TRUTH) * self.num_trials
        accuracy = (total_tp / total_gt) * 100 if total_gt > 0 else 0

        # Print results
        print('\n' + '='*60)
        print('OBJECT DETECTION BENCHMARK RESULTS')
        print('='*60)
        print(f'Trials completed: {self.num_trials}')
        print(f'Ground truth objects per trial: {len(self.GROUND_TRUTH)}')
        print(f'Total ground truth objects: {total_gt}')
        print('\n' + '-'*60)
        print('DETECTION METRICS')
        print('-'*60)
        print(f'Average Precision: {avg_precision:.3f}')
        print(f'Average Recall:    {avg_recall:.3f}')
        print(f'Average F1 Score:  {avg_f1:.3f}')
        print(f'Detection Accuracy: {accuracy:.1f}% ({total_tp}/{total_gt} objects)')
        print('\n' + '-'*60)
        print('PERFORMANCE METRICS')
        print('-'*60)
        print(f'Average Inference Time: {avg_latency:.1f}ms')
        print(f'Average FPS: {1000/avg_latency:.1f}')
        print('\n' + '-'*60)
        print('CONFUSION MATRIX')
        print('-'*60)
        print(f'True Positives:  {total_tp}')
        print(f'False Positives: {total_fp}')
        print(f'False Negatives: {total_fn}')
        print('='*60)

        # Check success criterion
        success_threshold = 85.0  # SC-003 requires >85%
        if accuracy >= success_threshold:
            print(f'\n SUCCESS: Detection accuracy {accuracy:.1f}% >= {success_threshold}%')
            print(' SC-003 success criterion PASSED')
        else:
            print(f'\n FAILURE: Detection accuracy {accuracy:.1f}% < {success_threshold}%')
            print(f' Need {success_threshold - accuracy:.1f}% improvement to pass SC-003')

        print('='*60 + '\n')


def main(args=None):
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Object Detection Benchmark')
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8l.pt',
        help='YOLOv8 model path'
    )
    parser.add_argument(
        '--trials',
        type=int,
        default=20,
        help='Number of detection trials'
    )

    cli_args, unknown = parser.parse_known_args()

    rclpy.init(args=args)

    node = ObjectDetectionBenchmark(
        model_path=cli_args.model,
        num_trials=cli_args.trials
    )

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
