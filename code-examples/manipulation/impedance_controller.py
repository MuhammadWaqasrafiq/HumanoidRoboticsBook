#!/usr/bin/env python3
"""
Cartesian Impedance Controller for Compliant Manipulation
=========================================================

Implements variable-stiffness Cartesian impedance control for safe,
compliant robot manipulation with force/torque feedback.

Author: Physical AI Book
License: MIT
Dependencies: numpy, scipy, rclpy
"""

import numpy as np
from scipy.spatial.transform import Rotation as R

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, WrenchStamped, TwistStamped
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class CartesianImpedanceController(Node):
    """
    ROS 2 node implementing Cartesian impedance control.

    Subscribes to:
        /target_pose (PoseStamped): Desired end-effector pose
        /joint_states (JointState): Current joint configuration
        /ft_sensor/wrench (WrenchStamped): Measured external forces/torques

    Publishes:
        /torque_commands (Float64MultiArray): Joint torque commands
        /ee_twist (TwistStamped): Current end-effector velocity
    """

    def __init__(self):
        super().__init__('impedance_controller')

        # Control parameters
        self.declare_parameter('stiffness_position', [300.0, 300.0, 300.0])  # N/m
        self.declare_parameter('stiffness_orientation', [30.0, 30.0, 30.0])  # Nm/rad
        self.declare_parameter('damping_position', [50.0, 50.0, 50.0])  # Ns/m
        self.declare_parameter('damping_orientation', [5.0, 5.0, 5.0])  # Nms/rad
        self.declare_parameter('control_rate', 200.0)  # Hz
        self.declare_parameter('adaptive_stiffness', True)

        # Load parameters
        K_pos = self.get_parameter('stiffness_position').value
        K_ori = self.get_parameter('stiffness_orientation').value
        D_pos = self.get_parameter('damping_position').value
        D_ori = self.get_parameter('damping_orientation').value
        control_rate = self.get_parameter('control_rate').value
        self.adaptive = self.get_parameter('adaptive_stiffness').value

        # Build stiffness and damping matrices
        self.K = np.diag(K_pos + K_ori)  # 6×6 diagonal
        self.D = np.diag(D_pos + D_ori)  # 6×6 diagonal

        # State variables
        self.n_joints = 7
        self.q = np.zeros(self.n_joints)
        self.dq = np.zeros(self.n_joints)
        self.target_pose = np.eye(4)
        self.current_pose = np.eye(4)
        self.f_external = np.zeros(6)

        # Subscribers
        self.target_sub = self.create_subscription(
            PoseStamped,
            '/target_pose',
            self.target_callback,
            10
        )

        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.ft_sub = self.create_subscription(
            WrenchStamped,
            '/ft_sensor/wrench',
            self.ft_callback,
            10
        )

        # Publishers
        self.torque_pub = self.create_publisher(Float64MultiArray, '/torque_commands', 10)
        self.twist_pub = self.create_publisher(TwistStamped, '/ee_twist', 10)

        # Control loop timer
        dt = 1.0 / control_rate
        self.timer = self.create_timer(dt, self.control_loop)

        self.get_logger().info(f'Impedance controller initialized (K_pos={K_pos}, rate={control_rate}Hz)')

    def target_callback(self, msg):
        """Update target pose"""
        self.target_pose = self.pose_stamped_to_transform(msg)

    def joint_state_callback(self, msg):
        """Update joint state"""
        if len(msg.position) >= self.n_joints:
            self.q = np.array(msg.position[:self.n_joints])
            if len(msg.velocity) >= self.n_joints:
                self.dq = np.array(msg.velocity[:self.n_joints])

    def ft_callback(self, msg):
        """Update external wrench measurement"""
        self.f_external = np.array([
            msg.wrench.force.x,
            msg.wrench.force.y,
            msg.wrench.force.z,
            msg.wrench.torque.x,
            msg.wrench.torque.y,
            msg.wrench.torque.z
        ])

    def control_loop(self):
        """
        Main impedance control loop (runs at control_rate Hz).

        Computes joint torques to achieve compliant behavior:
        τ = J^T · (K·Δx - D·ẋ - f_ext) + τ_gravity
        """
        # 1. Forward kinematics: compute current end-effector pose
        self.current_pose = self.forward_kinematics(self.q)

        # 2. Compute pose error (6D: position + orientation)
        x_error = self.compute_pose_error(self.target_pose, self.current_pose)

        # 3. Compute Jacobian and end-effector velocity
        J = self.compute_jacobian(self.q)  # 6×n
        x_dot = J @ self.dq  # Cartesian velocity

        # Publish for debugging
        self.publish_ee_twist(x_dot)

        # 4. Adaptive stiffness (optional)
        if self.adaptive:
            self.adapt_stiffness(self.f_external)

        # 5. Impedance control law (task space)
        f_desired = self.K @ x_error - self.D @ x_dot

        # 6. Compensate for external forces
        f_control = f_desired - self.f_external

        # 7. Map to joint torques via Jacobian transpose
        tau = J.T @ f_control

        # 8. Add gravity compensation
        tau_gravity = self.compute_gravity_torques(self.q)
        tau += tau_gravity

        # 9. Publish torque commands
        self.publish_torques(tau)

    def compute_pose_error(self, target, current):
        """
        Compute 6D pose error (position + orientation).

        Args:
            target, current (ndarray): 4x4 homogeneous transforms

        Returns:
            ndarray: 6D error [Δx, Δy, Δz, Δrx, Δry, Δrz]
        """
        # Position error
        pos_error = target[:3, 3] - current[:3, 3]

        # Orientation error (axis-angle)
        R_target = target[:3, :3]
        R_current = current[:3, :3]
        R_error = R_target @ R_current.T

        rot_error = R.from_matrix(R_error).as_rotvec()

        return np.concatenate([pos_error, rot_error])

    def adapt_stiffness(self, f_external):
        """
        Adapt stiffness based on contact forces.

        Strategy:
        - Free space (low force): High stiffness for precision
        - Contact (high force): Low stiffness for compliance

        Args:
            f_external (ndarray): Measured external wrench (6D)
        """
        force_magnitude = np.linalg.norm(f_external[:3])

        if force_magnitude &gt; 5.0:  # Contact detected (&gt;5N)
            # Compliant mode: soft in XY, moderate in Z
            K_pos = [50.0, 50.0, 100.0]
            K_ori = [10.0, 10.0, 10.0]
            self.get_logger().info('Contact detected - switching to compliant mode', throttle_duration_sec=1.0)
        elif force_magnitude &gt; 2.0:  # Light contact
            # Medium stiffness
            K_pos = [150.0, 150.0, 200.0]
            K_ori = [20.0, 20.0, 20.0]
        else:  # Free space
            # Stiff mode: precise position control
            K_pos = [300.0, 300.0, 300.0]
            K_ori = [30.0, 30.0, 30.0]

        self.K = np.diag(K_pos + K_ori)

        # Adjust damping (critically damped: D = 2√(M·K))
        # Assuming unit mass, D ≈ 2√K
        D_pos = [2 * np.sqrt(k) for k in K_pos]
        D_ori = [2 * np.sqrt(k) for k in K_ori]
        self.D = np.diag(D_pos + D_ori)

    def compute_gravity_torques(self, q):
        """
        Compute gravity compensation torques.

        For production, use:
        - Pinocchio: pinocchio.computeGeneralizedGravity(model, data, q)
        - KDL: ChainDynParam.JntToGravity(q, tau_g)

        Args:
            q (ndarray): Joint angles (n,)

        Returns:
            ndarray: Gravity torques (n,)
        """
        # Simplified gravity model (example: 7-DOF arm)
        # This should be computed from URDF mass/inertia properties

        g = 9.81  # m/s²
        link_masses = np.array([2.0, 2.0, 2.0, 1.5, 1.0, 0.5, 0.2])  # kg (example)

        # Simplified: τ_g ≈ J^T · [0, 0, -m_total·g, 0, 0, 0]
        # For accurate gravity, use recursive Newton-Euler or URDF dynamics

        J = self.compute_jacobian(q)
        gravity_wrench = np.array([0, 0, -np.sum(link_masses) * g, 0, 0, 0])

        tau_gravity = J.T @ gravity_wrench

        return tau_gravity

    def forward_kinematics(self, q):
        """
        Forward kinematics (simplified - replace with URDF model).

        See ik_solver.py for example implementation.
        """
        # Placeholder: use same FK as IK solver
        # In production, load from URDF
        T = np.eye(4)

        # (Add your robot's DH chain here - see ik_solver.py)
        # For now, return identity (replace in production)

        return T

    def compute_jacobian(self, q):
        """
        Compute geometric Jacobian (simplified - replace with URDF model).

        See ik_solver.py for example implementation.
        """
        # Placeholder: 6×7 identity (replace in production)
        J = np.eye(6, self.n_joints)

        return J

    def publish_torques(self, tau):
        """Publish joint torque commands"""
        msg = Float64MultiArray()
        msg.data = tau.tolist()

        self.torque_pub.publish(msg)

    def publish_ee_twist(self, x_dot):
        """Publish end-effector velocity for monitoring"""
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        msg.twist.linear.x = x_dot[0]
        msg.twist.linear.y = x_dot[1]
        msg.twist.linear.z = x_dot[2]
        msg.twist.angular.x = x_dot[3]
        msg.twist.angular.y = x_dot[4]
        msg.twist.angular.z = x_dot[5]

        self.twist_pub.publish(msg)

    @staticmethod
    def pose_stamped_to_transform(msg):
        """Convert PoseStamped to 4x4 homogeneous transform"""
        T = np.eye(4)

        T[0, 3] = msg.pose.position.x
        T[1, 3] = msg.pose.position.y
        T[2, 3] = msg.pose.position.z

        quat = [
            msg.pose.orientation.x,
            msg.pose.orientation.y,
            msg.pose.orientation.z,
            msg.pose.orientation.w
        ]
        T[:3, :3] = R.from_quat(quat).as_matrix()

        return T


def main(args=None):
    """Main entry point"""
    rclpy.init(args=args)

    controller = CartesianImpedanceController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
