#!/usr/bin/env python3
"""
RGB-D Camera Subscriber Node for ROS 2 Iron

Subscribes to Intel RealSense D455 camera topics and processes RGB-D data.
Demonstrates proper camera integration patterns for humanoid perception.

Dependencies:
    - ROS 2 Iron
    - Intel RealSense SDK 2.0
    - OpenCV 4.x
    - NumPy

Usage:
    # Terminal 1: Launch RealSense camera
    ros2 launch realsense2_camera rs_launch.py enable_depth:=true

    # Terminal 2: Run this subscriber
    python3 camera_subscriber.py

Author: Physical AI Robotics Book
License: MIT
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np
from typing import Optional


class RGBDCameraSubscriber(Node):
    """
    Subscribes to RGB and depth images from RealSense D455 camera.

    Processes aligned RGB-D frames for downstream perception tasks.
    """

    def __init__(self):
        super().__init__('rgbd_camera_subscriber')

        # Initialize CV bridge for ROS-OpenCV conversion
        self.bridge = CvBridge()

        # Camera intrinsics (will be updated from CameraInfo)
        self.camera_matrix: Optional[np.ndarray] = None
        self.dist_coeffs: Optional[np.ndarray] = None

        # Latest frame storage
        self.latest_rgb: Optional[np.ndarray] = None
        self.latest_depth: Optional[np.ndarray] = None

        # Frame counters for diagnostics
        self.rgb_frame_count = 0
        self.depth_frame_count = 0

        # Subscribe to camera topics
        self.rgb_sub = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.rgb_callback,
            10  # QoS depth
        )

        self.depth_sub = self.create_subscription(
            Image,
            '/camera/aligned_depth_to_color/image_raw',
            self.depth_callback,
            10
        )

        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/color/camera_info',
            self.camera_info_callback,
            10
        )

        # Timer for processing pipeline (30 Hz)
        self.create_timer(1.0 / 30.0, self.process_rgbd_frame)

        # Timer for diagnostics (1 Hz)
        self.create_timer(1.0, self.print_diagnostics)

        self.get_logger().info('RGB-D Camera Subscriber initialized')
        self.get_logger().info('Waiting for camera topics...')

    def camera_info_callback(self, msg: CameraInfo) -> None:
        """Extract camera intrinsics from CameraInfo message."""
        if self.camera_matrix is None:
            # Camera matrix (3x3)
            self.camera_matrix = np.array(msg.k).reshape(3, 3)

            # Distortion coefficients
            self.dist_coeffs = np.array(msg.d)

            self.get_logger().info(f'Camera intrinsics received:')
            self.get_logger().info(f'  Resolution: {msg.width}x{msg.height}')
            self.get_logger().info(f'  fx: {self.camera_matrix[0, 0]:.2f}')
            self.get_logger().info(f'  fy: {self.camera_matrix[1, 1]:.2f}')
            self.get_logger().info(f'  cx: {self.camera_matrix[0, 2]:.2f}')
            self.get_logger().info(f'  cy: {self.camera_matrix[1, 2]:.2f}')

    def rgb_callback(self, msg: Image) -> None:
        """Process RGB image from camera."""
        try:
            # Convert ROS Image to OpenCV format (BGR8)
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.latest_rgb = cv_image
            self.rgb_frame_count += 1

        except Exception as e:
            self.get_logger().error(f'RGB conversion failed: {e}')

    def depth_callback(self, msg: Image) -> None:
        """Process depth image from camera."""
        try:
            # Convert ROS depth image to OpenCV format (16-bit unsigned)
            # Depth values are in millimeters
            cv_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='16UC1')
            self.latest_depth = cv_depth
            self.depth_frame_count += 1

        except Exception as e:
            self.get_logger().error(f'Depth conversion failed: {e}')

    def process_rgbd_frame(self) -> None:
        """
        Main processing loop for synchronized RGB-D frames.

        This is where you would add perception algorithms:
        - Object detection (YOLOv8)
        - Depth processing
        - Point cloud generation
        - Feature extraction
        """
        if self.latest_rgb is None or self.latest_depth is None:
            return  # Wait until both frames available

        # Get latest synchronized frames
        rgb_frame = self.latest_rgb.copy()
        depth_frame = self.latest_depth.copy()

        # Example: Visualize RGB with depth overlay
        depth_colormap = self.create_depth_colormap(depth_frame)

        # Create side-by-side visualization
        h, w = rgb_frame.shape[:2]
        display = np.hstack([rgb_frame, depth_colormap])

        # Add FPS counter
        cv2.putText(
            display,
            f'RGB: {self.rgb_frame_count} frames',
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            display,
            f'Depth: {self.depth_frame_count} frames',
            (w + 10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Display result
        cv2.imshow('RGB-D Stream', display)
        cv2.waitKey(1)

        # Example: Get depth at center pixel
        center_x, center_y = w // 2, h // 2
        center_depth = depth_frame[center_y, center_x]

        if center_depth > 0:  # Valid depth
            depth_meters = center_depth / 1000.0  # Convert mm to meters

            # Draw crosshair on RGB
            cv2.circle(rgb_frame, (center_x, center_y), 5, (0, 0, 255), -1)

            # Optional: Project to 3D using camera intrinsics
            if self.camera_matrix is not None:
                x_3d, y_3d, z_3d = self.pixel_to_3d(
                    center_x, center_y, depth_meters
                )
                self.get_logger().debug(
                    f'Center pixel 3D: ({x_3d:.3f}, {y_3d:.3f}, {z_3d:.3f})'
                )

    def create_depth_colormap(self, depth_image: np.ndarray) -> np.ndarray:
        """
        Convert depth image to colormap for visualization.

        Args:
            depth_image: Depth image in millimeters (16-bit)

        Returns:
            Colorized depth image (BGR8)
        """
        # Clip depth to realistic range (0.3m to 6m for RealSense D455)
        depth_clipped = np.clip(depth_image, 300, 6000)

        # Normalize to 0-255
        depth_normalized = ((depth_clipped - 300) / (6000 - 300) * 255).astype(np.uint8)

        # Apply colormap (COLORMAP_JET: blue=far, red=close)
        depth_colormap = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

        # Mask invalid pixels (depth=0) as black
        depth_colormap[depth_image == 0] = 0

        return depth_colormap

    def pixel_to_3d(self, u: int, v: int, depth: float) -> tuple[float, float, float]:
        """
        Convert pixel coordinates and depth to 3D point.

        Args:
            u: Pixel x coordinate
            v: Pixel y coordinate
            depth: Depth in meters

        Returns:
            (X, Y, Z) in camera frame (meters)
        """
        if self.camera_matrix is None:
            raise ValueError('Camera intrinsics not available')

        fx = self.camera_matrix[0, 0]
        fy = self.camera_matrix[1, 1]
        cx = self.camera_matrix[0, 2]
        cy = self.camera_matrix[1, 2]

        # Pinhole camera model
        X = (u - cx) * depth / fx
        Y = (v - cy) * depth / fy
        Z = depth

        return X, Y, Z

    def print_diagnostics(self) -> None:
        """Print diagnostic information every second."""
        if self.latest_rgb is not None and self.latest_depth is not None:
            h, w = self.latest_rgb.shape[:2]

            # Calculate depth statistics
            valid_depth = self.latest_depth[self.latest_depth > 0]
            if len(valid_depth) > 0:
                min_depth = valid_depth.min() / 1000.0
                max_depth = valid_depth.max() / 1000.0
                mean_depth = valid_depth.mean() / 1000.0

                self.get_logger().info(
                    f'Depth stats - Min: {min_depth:.2f}m, '
                    f'Max: {max_depth:.2f}m, Mean: {mean_depth:.2f}m'
                )


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)

    node = RGBDCameraSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
