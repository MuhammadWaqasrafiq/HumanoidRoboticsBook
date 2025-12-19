#!/usr/bin/env python3
"""
Depth Image to Point Cloud Processor for ROS 2

Converts aligned RGB-D images to 3D point clouds with color.
Implements filtering, downsampling, and outlier removal for clean point clouds.

Dependencies:
    - ROS 2 Iron
    - Open3D 0.18+
    - NumPy
    - sensor_msgs

Usage:
    # Terminal 1: Launch camera
    ros2 launch realsense2_camera rs_launch.py enable_depth:=true

    # Terminal 2: Run depth processor
    python3 depth_processor.py

    # Terminal 3: Visualize in RViz2
    rviz2 -d config/pointcloud_viz.rviz

Author: Physical AI Robotics Book
License: MIT
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo, PointCloud2, PointField
from std_msgs.msg import Header
from cv_bridge import CvBridge
import numpy as np
import open3d as o3d
import struct
from typing import Optional


class DepthProcessor(Node):
    """
    Processes depth images and publishes 3D point clouds.

    Features:
    - Depth-to-point-cloud conversion
    - Voxel downsampling (1M points → 50K)
    - Statistical outlier removal
    - Color from aligned RGB
    """

    def __init__(self):
        super().__init__('depth_processor')

        # Parameters
        self.declare_parameter('min_depth', 0.3)   # meters
        self.declare_parameter('max_depth', 6.0)   # meters
        self.declare_parameter('voxel_size', 0.01) # 1cm voxels
        self.declare_parameter('outlier_nb_neighbors', 20)
        self.declare_parameter('outlier_std_ratio', 2.0)

        # Get parameters
        self.min_depth = self.get_parameter('min_depth').value
        self.max_depth = self.get_parameter('max_depth').value
        self.voxel_size = self.get_parameter('voxel_size').value
        self.outlier_nb = self.get_parameter('outlier_nb_neighbors').value
        self.outlier_std = self.get_parameter('outlier_std_ratio').value

        # CV bridge
        self.bridge = CvBridge()

        # Camera intrinsics
        self.camera_matrix: Optional[np.ndarray] = None
        self.fx: Optional[float] = None
        self.fy: Optional[float] = None
        self.cx: Optional[float] = None
        self.cy: Optional[float] = None

        # Latest frames
        self.latest_rgb: Optional[np.ndarray] = None
        self.latest_depth: Optional[np.ndarray] = None

        # Statistics
        self.total_points_processed = 0
        self.total_points_output = 0

        # Subscribers
        self.rgb_sub = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.rgb_callback,
            10
        )

        self.depth_sub = self.create_subscription(
            Image,
            '/camera/aligned_depth_to_color/image_raw',
            self.depth_callback,
            10
        )

        self.info_sub = self.create_subscription(
            CameraInfo,
            '/camera/color/camera_info',
            self.info_callback,
            10
        )

        # Publisher for point cloud
        self.pointcloud_pub = self.create_publisher(
            PointCloud2,
            '/camera/pointcloud',
            10
        )

        # Processing timer (30 Hz)
        self.create_timer(1.0 / 30.0, self.process_pointcloud)

        # Diagnostics timer (1 Hz)
        self.create_timer(1.0, self.print_diagnostics)

        self.get_logger().info('Depth Processor initialized')
        self.get_logger().info(f'Depth range: {self.min_depth}m - {self.max_depth}m')
        self.get_logger().info(f'Voxel size: {self.voxel_size}m')

    def info_callback(self, msg: CameraInfo) -> None:
        """Extract camera intrinsics."""
        if self.camera_matrix is None:
            self.camera_matrix = np.array(msg.k).reshape(3, 3)
            self.fx = self.camera_matrix[0, 0]
            self.fy = self.camera_matrix[1, 1]
            self.cx = self.camera_matrix[0, 2]
            self.cy = self.camera_matrix[1, 2]

            self.get_logger().info('Camera intrinsics received')

    def rgb_callback(self, msg: Image) -> None:
        """Store latest RGB image."""
        try:
            self.latest_rgb = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'RGB conversion error: {e}')

    def depth_callback(self, msg: Image) -> None:
        """Store latest depth image."""
        try:
            self.latest_depth = self.bridge.imgmsg_to_cv2(msg, '16UC1')
        except Exception as e:
            self.get_logger().error(f'Depth conversion error: {e}')

    def process_pointcloud(self) -> None:
        """Main point cloud processing pipeline."""
        # Check if all data available
        if (self.latest_rgb is None or
            self.latest_depth is None or
            self.camera_matrix is None):
            return

        # Step 1: Convert depth to point cloud
        points, colors = self.depth_to_pointcloud(
            self.latest_depth,
            self.latest_rgb
        )

        if points is None or len(points) == 0:
            return

        self.total_points_processed += len(points)

        # Step 2: Create Open3D point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.colors = o3d.utility.Vector3dVector(colors)

        # Step 3: Voxel downsampling
        pcd_downsampled = pcd.voxel_down_sample(self.voxel_size)

        # Step 4: Statistical outlier removal
        pcd_filtered, _ = pcd_downsampled.remove_statistical_outlier(
            nb_neighbors=self.outlier_nb,
            std_ratio=self.outlier_std
        )

        # Step 5: Convert to ROS PointCloud2
        pointcloud_msg = self.o3d_to_ros_pointcloud2(
            pcd_filtered,
            frame_id='camera_color_optical_frame'
        )

        # Publish
        self.pointcloud_pub.publish(pointcloud_msg)

        self.total_points_output += len(pcd_filtered.points)

    def depth_to_pointcloud(
        self,
        depth_image: np.ndarray,
        rgb_image: np.ndarray
    ) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Convert depth image to 3D point cloud with RGB colors.

        Args:
            depth_image: Depth in millimeters (H, W) uint16
            rgb_image: RGB image (H, W, 3) uint8

        Returns:
            points: (N, 3) XYZ coordinates in meters
            colors: (N, 3) RGB values in [0, 1]
        """
        h, w = depth_image.shape

        # Create pixel coordinate grids
        u_grid, v_grid = np.meshgrid(np.arange(w), np.arange(h))

        # Convert depth from mm to meters
        depth_m = depth_image.astype(np.float32) / 1000.0

        # Filter by depth range
        valid_mask = (depth_m >= self.min_depth) & (depth_m <= self.max_depth)

        # Extract valid pixels
        u_valid = u_grid[valid_mask]
        v_valid = v_grid[valid_mask]
        z_valid = depth_m[valid_mask]

        if len(z_valid) == 0:
            return None, None

        # Project to 3D using pinhole camera model
        x = (u_valid - self.cx) * z_valid / self.fx
        y = (v_valid - self.cy) * z_valid / self.fy
        z = z_valid

        # Stack into (N, 3) points
        points = np.stack([x, y, z], axis=-1)

        # Extract RGB colors for valid points
        rgb_valid = rgb_image[valid_mask]

        # Convert BGR to RGB and normalize to [0, 1]
        colors = rgb_valid[:, ::-1].astype(np.float32) / 255.0

        return points, colors

    def o3d_to_ros_pointcloud2(
        self,
        pcd: o3d.geometry.PointCloud,
        frame_id: str
    ) -> PointCloud2:
        """
        Convert Open3D point cloud to ROS PointCloud2 message.

        Args:
            pcd: Open3D PointCloud with XYZ and RGB
            frame_id: TF frame name

        Returns:
            ROS PointCloud2 message
        """
        points = np.asarray(pcd.points)
        colors = np.asarray(pcd.colors)

        # Define PointCloud2 fields (XYZ + RGB)
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name='rgb', offset=12, datatype=PointField.FLOAT32, count=1),
        ]

        # Pack RGB into single float32
        rgb_int = (colors[:, 0] * 255).astype(np.uint32) << 16 | \
                  (colors[:, 1] * 255).astype(np.uint32) << 8 | \
                  (colors[:, 2] * 255).astype(np.uint32)
        rgb_float = rgb_int.view(np.float32)

        # Combine XYZ and RGB
        cloud_data = np.column_stack([points, rgb_float])

        # Create PointCloud2 message
        msg = PointCloud2()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame_id

        msg.height = 1
        msg.width = len(points)
        msg.fields = fields
        msg.is_bigendian = False
        msg.point_step = 16  # 4 floats * 4 bytes
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = True
        msg.data = cloud_data.tobytes()

        return msg

    def print_diagnostics(self) -> None:
        """Print processing statistics."""
        if self.total_points_processed > 0:
            reduction_ratio = (1 - self.total_points_output / self.total_points_processed) * 100

            self.get_logger().info(
                f'Point cloud stats - '
                f'Input: {self.total_points_processed:,} points, '
                f'Output: {self.total_points_output:,} points '
                f'(Reduction: {reduction_ratio:.1f}%)'
            )

            # Reset counters
            self.total_points_processed = 0
            self.total_points_output = 0


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)

    node = DepthProcessor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
