#!/usr/bin/env python3
"""
Grasp Planner - Antipodal Grasp Generation for Robotic Manipulation
==================================================================

This module implements antipodal grasp planning for parallel-jaw grippers.
It generates grasp candidates from point cloud data and ranks them using
the Ferrari-Canny quality metric.

Author: Physical AI Book
License: MIT
Dependencies: numpy, scipy, open3d, rclpy
"""

import numpy as np
from scipy.spatial.distance import cdist
from scipy.spatial import ConvexHull
import open3d as o3d

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import MarkerArray, Marker

class GraspPlanner(Node):
    """
    ROS 2 node for generating and ranking antipodal grasps from point clouds.

    Subscribes to:
        /camera/points (sensor_msgs/PointCloud2): Input point cloud from RGB-D camera

    Publishes:
        /grasp_candidates (visualization_msgs/MarkerArray): Top-k grasp visualizations
        /best_grasp (geometry_msgs/PoseStamped): Highest-quality grasp pose
    """

    def __init__(self):
        super().__init__('grasp_planner')

        # Parameters
        self.declare_parameter('gripper_width', 0.08)  # Max gripper opening (meters)
        self.declare_parameter('friction_coeff', 0.7)  # Surface friction coefficient
        self.declare_parameter('min_quality', 0.3)  # Minimum grasp quality threshold
        self.declare_parameter('top_k', 10)  # Number of grasp candidates to return

        self.gripper_width = self.get_parameter('gripper_width').value
        self.friction_coeff = self.get_parameter('friction_coeff').value
        self.min_quality = self.get_parameter('min_quality').value
        self.top_k = self.get_parameter('top_k').value

        # Subscribers
        self.pc_sub = self.create_subscription(
            PointCloud2,
            '/camera/points',
            self.pointcloud_callback,
            10
        )

        # Publishers
        self.grasp_viz_pub = self.create_publisher(MarkerArray, '/grasp_candidates', 10)
        self.best_grasp_pub = self.create_publisher(PoseStamped, '/best_grasp', 10)

        self.get_logger().info(f'Grasp planner initialized (width={self.gripper_width}m, μ={self.friction_coeff})')

    def pointcloud_callback(self, msg):
        """Process incoming point cloud and generate grasps"""
        # Convert ROS PointCloud2 to numpy array
        points = self.pointcloud2_to_array(msg)

        if len(points) &lt; 100:
            self.get_logger().warn('Insufficient points in cloud, skipping grasp planning')
            return

        # Downsample and compute normals
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd = pcd.voxel_down_sample(voxel_size=0.005)  # 5mm voxels
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.01, max_nn=30))

        points_np = np.asarray(pcd.points)
        normals_np = np.asarray(pcd.normals)

        # Generate grasp candidates
        grasps = self.generate_antipodal_grasps(points_np, normals_np)

        if len(grasps) == 0:
            self.get_logger().warn('No valid grasps found')
            return

        # Publish visualizations
        self.publish_grasp_markers(grasps, msg.header)

        # Publish best grasp pose
        best_grasp = grasps[0]
        pose_msg = self.grasp_to_pose_stamped(best_grasp, msg.header)
        self.best_grasp_pub.publish(pose_msg)

        self.get_logger().info(f'Generated {len(grasps)} grasps, best quality: {best_grasp["quality"]:.3f}')

    def generate_antipodal_grasps(self, point_cloud, normals):
        """
        Generate antipodal grasp candidates using contact point sampling.

        Args:
            point_cloud (ndarray): Nx3 array of 3D points
            normals (ndarray): Nx3 array of surface normals

        Returns:
            list: Sorted list of grasp dictionaries (best first)
        """
        grasps = []
        n_points = len(point_cloud)

        # Sample subset of points for efficiency (every 10th point)
        sample_indices = np.arange(0, n_points, 10)

        for i in sample_indices:
            p1 = point_cloud[i]
            n1 = normals[i]

            # Find opposing contact points within gripper width
            distances = cdist([p1], point_cloud)[0]
            candidates = np.where((distances &gt; 0.02) & (distances &lt; self.gripper_width))[0]

            for j in candidates:
                if j &lt;= i:  # Avoid duplicates
                    continue

                p2 = point_cloud[j]
                n2 = normals[j]

                # Compute grasp axis (line connecting contact points)
                grasp_axis = (p2 - p1) / np.linalg.norm(p2 - p1)

                # Check antipodal condition: normals oppose and align with grasp axis
                alignment1 = np.dot(n1, grasp_axis)
                alignment2 = np.dot(n2, -grasp_axis)

                # Both normals should point toward each other (cos θ &gt; 0.95 → θ &lt; 18°)
                if alignment1 &gt; 0.95 and alignment2 &gt; 0.95:
                    # Compute grasp center and orientation
                    center = (p1 + p2) / 2
                    width = distances[j]

                    # Compute approach direction (perpendicular to grasp axis)
                    approach = np.cross(grasp_axis, [0, 0, 1])  # Assume Z-up
                    if np.linalg.norm(approach) &lt; 0.1:  # grasp_axis parallel to Z
                        approach = np.cross(grasp_axis, [1, 0, 0])
                    approach /= np.linalg.norm(approach)

                    # Compute grasp quality (Ferrari-Canny approximation)
                    quality = self.compute_grasp_quality(p1, p2, n1, n2, width)

                    if quality &gt; self.min_quality:
                        grasps.append({
                            'p1': p1,
                            'p2': p2,
                            'center': center,
                            'axis': grasp_axis,
                            'approach': approach,
                            'width': width,
                            'quality': quality
                        })

        # Sort by quality (descending) and return top-k
        grasps.sort(key=lambda g: g['quality'], reverse=True)
        return grasps[:self.top_k]

    def compute_grasp_quality(self, p1, p2, n1, n2, width):
        """
        Compute Ferrari-Canny grasp quality metric (simplified).

        Quality combines:
        1. Normal alignment (how well normals oppose)
        2. Width utilization (grasps near max width are less stable)
        3. Force closure approximation

        Args:
            p1, p2 (ndarray): Contact points
            n1, n2 (ndarray): Contact normals
            width (float): Grasp width (distance between contacts)

        Returns:
            float: Grasp quality [0, 1] (higher = better)
        """
        # Grasp axis
        grasp_axis = (p2 - p1) / np.linalg.norm(p2 - p1)

        # Normal alignment quality (both normals should point inward)
        alignment1 = np.dot(n1, grasp_axis)
        alignment2 = np.dot(n2, -grasp_axis)
        alignment_quality = min(alignment1, alignment2)

        # Width utilization (prefer narrower grasps for stability)
        width_quality = 1.0 - (width / self.gripper_width)

        # Wrench space quality (simplified force closure check)
        # For 2-contact grasp, check if friction cone spans task space
        friction_angle = np.arctan(self.friction_coeff)  # Friction cone half-angle

        # Quality decreases if normals are too aligned (poor wrench space coverage)
        normal_angle = np.arccos(np.clip(np.dot(n1, -n2), -1, 1))
        wrench_quality = np.clip(normal_angle / np.pi, 0, 1)

        # Combined quality (weighted average)
        quality = (
            0.5 * alignment_quality +
            0.3 * width_quality +
            0.2 * wrench_quality
        )

        return quality

    def grasp_to_pose_stamped(self, grasp, header):
        """Convert grasp dict to PoseStamped message"""
        pose = PoseStamped()
        pose.header = header

        # Position: grasp center
        pose.pose.position.x = grasp['center'][0]
        pose.pose.position.y = grasp['center'][1]
        pose.pose.position.z = grasp['center'][2]

        # Orientation: align gripper with grasp axis
        # X-axis: grasp axis (opening direction)
        # Y-axis: approach direction
        # Z-axis: perpendicular (computed from cross product)
        x_axis = grasp['axis']
        y_axis = grasp['approach']
        z_axis = np.cross(x_axis, y_axis)

        # Construct rotation matrix
        R = np.column_stack([x_axis, y_axis, z_axis])

        # Convert to quaternion (simplified)
        qw = np.sqrt(1 + R[0, 0] + R[1, 1] + R[2, 2]) / 2
        qx = (R[2, 1] - R[1, 2]) / (4 * qw)
        qy = (R[0, 2] - R[2, 0]) / (4 * qw)
        qz = (R[1, 0] - R[0, 1]) / (4 * qw)

        pose.pose.orientation.w = qw
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz

        return pose

    def publish_grasp_markers(self, grasps, header):
        """Publish grasp visualization markers"""
        marker_array = MarkerArray()

        for i, grasp in enumerate(grasps):
            # Gripper marker (cylinder between contact points)
            marker = Marker()
            marker.header = header
            marker.ns = "grasps"
            marker.id = i
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD

            # Position: grasp center
            marker.pose.position.x = grasp['center'][0]
            marker.pose.position.y = grasp['center'][1]
            marker.pose.position.z = grasp['center'][2]

            # Orientation: align with grasp axis
            marker.pose.orientation.x = 0.0
            marker.pose.orientation.y = 0.0
            marker.pose.orientation.z = 0.0
            marker.pose.orientation.w = 1.0

            # Scale: width and finger thickness
            marker.scale.x = 0.01  # Finger diameter
            marker.scale.y = 0.01
            marker.scale.z = grasp['width']

            # Color: green (high quality) to red (low quality)
            marker.color.r = 1.0 - grasp['quality']
            marker.color.g = grasp['quality']
            marker.color.b = 0.0
            marker.color.a = 0.8

            marker.lifetime.sec = 5

            marker_array.markers.append(marker)

        self.grasp_viz_pub.publish(marker_array)

    @staticmethod
    def pointcloud2_to_array(cloud_msg):
        """Convert ROS PointCloud2 to numpy array (XYZ only)"""
        # Simplified conversion (assumes PointXYZ format)
        # For production, use ros2_numpy or sensor_msgs_py
        import struct

        points = []
        point_step = cloud_msg.point_step
        row_step = cloud_msg.row_step

        for v in range(cloud_msg.height):
            for u in range(cloud_msg.width):
                offset = v * row_step + u * point_step
                x, y, z = struct.unpack_from('fff', cloud_msg.data, offset)

                if not (np.isnan(x) or np.isnan(y) or np.isnan(z)):
                    points.append([x, y, z])

        return np.array(points)


def main(args=None):
    """Main entry point"""
    rclpy.init(args=args)

    grasp_planner = GraspPlanner()

    try:
        rclpy.spin(grasp_planner)
    except KeyboardInterrupt:
        pass
    finally:
        grasp_planner.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
