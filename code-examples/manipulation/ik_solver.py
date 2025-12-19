#!/usr/bin/env python3
"""
Numerical Inverse Kinematics Solver
===================================

Implements damped least squares (Levenberg-Marquardt) IK solver for
robotic manipulators. Handles redundant arms and avoids singularities.

Author: Physical AI Book
License: MIT
Dependencies: numpy, scipy, urdfpy
"""

import numpy as np
from scipy.spatial.transform import Rotation as R

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger


class NumericalIKSolver(Node):
    """
    ROS 2 node providing numerical IK solving service.

    Services:
        /ik_solver/solve (std_srvs/Trigger): Solve IK for target pose
    """

    def __init__(self):
        super().__init__('numerical_ik_solver')

        # Parameters
        self.declare_parameter('robot_description', '')
        self.declare_parameter('end_effector_link', 'ee_link')
        self.declare_parameter('base_link', 'base_link')
        self.declare_parameter('lambda_damping', 0.05)
        self.declare_parameter('max_iterations', 100)
        self.declare_parameter('position_tolerance', 1e-4)  # 0.1mm
        self.declare_parameter('orientation_tolerance', 1e-3)  # ~0.06°

        self.end_effector = self.get_parameter('end_effector_link').value
        self.base_link = self.get_parameter('base_link').value
        self.lambda_damp = self.get_parameter('lambda_damping').value
        self.max_iter = self.get_parameter('max_iterations').value
        self.pos_tol = self.get_parameter('position_tolerance').value
        self.ori_tol = self.get_parameter('orientation_tolerance').value

        # Robot model (simplified - use urdfpy or robot_state_publisher in production)
        self.n_joints = 7  # Example: 7-DOF arm
        self.joint_limits_lower = np.array([-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973])
        self.joint_limits_upper = np.array([2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973])

        # Current joint state
        self.q_current = np.zeros(self.n_joints)
        self.target_pose = None

        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.target_pose_sub = self.create_subscription(
            PoseStamped,
            '/ik_target',
            self.target_pose_callback,
            10
        )

        # Publishers
        self.solution_pub = self.create_publisher(JointState, '/ik_solution', 10)

        self.get_logger().info(f'IK solver initialized (λ={self.lambda_damp}, max_iter={self.max_iter})')

    def joint_state_callback(self, msg):
        """Update current joint configuration"""
        if len(msg.position) >= self.n_joints:
            self.q_current = np.array(msg.position[:self.n_joints])

    def target_pose_callback(self, msg):
        """Solve IK when new target pose is received"""
        self.target_pose = self.pose_stamped_to_transform(msg)

        # Solve IK
        q_solution, success, error = self.solve_ik(self.target_pose, self.q_current)

        if success:
            self.get_logger().info(f'IK converged in {error["iterations"]} iterations (error: {error["final_error"]:.6f}m)')
            self.publish_solution(q_solution)
        else:
            self.get_logger().warn(f'IK failed to converge (error: {error["final_error"]:.4f}m)')

    def solve_ik(self, target_transform, q_init, verbose=False):
        """
        Solve inverse kinematics using damped least squares.

        Args:
            target_transform (ndarray): 4x4 homogeneous target pose
            q_init (ndarray): Initial joint angles (n,)
            verbose (bool): Print iteration details

        Returns:
            tuple: (q_solution, success, error_info)
                q_solution: Joint angles achieving target (or best effort)
                success: True if converged within tolerance
                error_info: Dict with convergence metrics
        """
        q = q_init.copy()

        for iteration in range(self.max_iter):
            # Forward kinematics: compute current end-effector pose
            current_transform = self.forward_kinematics(q)

            # Compute pose error (6D: position + orientation)
            pos_error = target_transform[:3, 3] - current_transform[:3, 3]
            rot_error = self.rotation_error(target_transform[:3, :3], current_transform[:3, :3])

            error = np.concatenate([pos_error, rot_error])
            error_norm = np.linalg.norm(error)

            # Check convergence
            if error_norm &lt; self.pos_tol:
                return q, True, {'iterations': iteration, 'final_error': error_norm}

            # Compute Jacobian at current configuration
            J = self.compute_jacobian(q)  # 6×n

            # Damped least squares update
            JtJ = J.T @ J
            damping_matrix = self.lambda_damp * np.eye(self.n_joints)

            try:
                delta_q = np.linalg.solve(JtJ + damping_matrix, J.T @ error)
            except np.linalg.LinAlgError:
                self.get_logger().error('Jacobian singular, aborting IK')
                return q, False, {'iterations': iteration, 'final_error': error_norm}

            # Update joint angles
            q += delta_q

            # Enforce joint limits
            q = np.clip(q, self.joint_limits_lower, self.joint_limits_upper)

            if verbose and iteration % 10 == 0:
                self.get_logger().info(f'Iteration {iteration}: error = {error_norm:.6f}m')

        # Max iterations reached without convergence
        return q, False, {'iterations': self.max_iter, 'final_error': error_norm}

    def forward_kinematics(self, q):
        """
        Compute forward kinematics (base → end-effector).

        This is a simplified kinematic chain. In production, use:
        - urdfpy: robot.link_fk(q)
        - KDL: ChainFkSolverPos
        - Pinocchio: pinocchio.forwardKinematics(model, data, q)

        Args:
            q (ndarray): Joint angles (n,)

        Returns:
            ndarray: 4x4 homogeneous transform
        """
        # Example: Simple 7-DOF arm kinematic chain (DH parameters)
        # This is robot-specific - replace with your URDF model

        T = np.eye(4)

        # Simplified kinematic chain (example: Panda-like arm)
        # Joint 1: Revolute Z, offset (0, 0, 0.333)
        T = T @ self.dh_transform(0, 0, 0.333, q[0])

        # Joint 2: Revolute Z, offset (0, 0, 0), rotation π/2
        T = T @ self.dh_transform(0, -np.pi/2, 0, q[1])

        # Joint 3: Revolute Z, offset (0, 0, 0.316)
        T = T @ self.dh_transform(0, np.pi/2, 0.316, q[2])

        # Joint 4: Revolute Z
        T = T @ self.dh_transform(0.0825, np.pi/2, 0, q[3])

        # Joint 5: Revolute Z
        T = T @ self.dh_transform(-0.0825, -np.pi/2, 0.384, q[4])

        # Joint 6: Revolute Z
        T = T @ self.dh_transform(0, np.pi/2, 0, q[5])

        # Joint 7: Revolute Z, end-effector offset
        T = T @ self.dh_transform(0.088, 0, 0, q[6])
        T = T @ self.dh_transform(0, 0, 0.107, 0)  # Flange offset

        return T

    @staticmethod
    def dh_transform(a, alpha, d, theta):
        """
        Compute Denavit-Hartenberg transformation matrix.

        Args:
            a, alpha, d, theta: DH parameters

        Returns:
            ndarray: 4x4 transformation matrix
        """
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(alpha)
        sa = np.sin(alpha)

        return np.array([
            [ct,    -st,    0,      a],
            [st*ca, ct*ca,  -sa,    -sa*d],
            [st*sa, ct*sa,  ca,     ca*d],
            [0,     0,      0,      1]
        ])

    def compute_jacobian(self, q):
        """
        Compute geometric Jacobian (6×n) using finite differences.

        For production, use analytic Jacobian from URDF:
        - urdfpy: robot.jacobian(q, link_name)
        - KDL: ChainJntToJacSolver
        - Pinocchio: pinocchio.computeJointJacobians(model, data, q)

        Args:
            q (ndarray): Joint angles (n,)

        Returns:
            ndarray: Jacobian matrix (6×n)
        """
        J = np.zeros((6, self.n_joints))
        epsilon = 1e-6

        # Current end-effector pose
        T0 = self.forward_kinematics(q)
        p0 = T0[:3, 3]
        R0 = T0[:3, :3]

        for i in range(self.n_joints):
            # Perturb joint i
            q_perturbed = q.copy()
            q_perturbed[i] += epsilon

            # Compute perturbed pose
            T1 = self.forward_kinematics(q_perturbed)
            p1 = T1[:3, 3]
            R1 = T1[:3, :3]

            # Linear velocity Jacobian (position derivative)
            J[:3, i] = (p1 - p0) / epsilon

            # Angular velocity Jacobian (orientation derivative)
            # dR = R1 @ R0.T ≈ I + [ω]× * dt
            # Extract ω from skew-symmetric matrix
            dR = R1 @ R0.T
            omega = np.array([
                dR[2, 1] - dR[1, 2],
                dR[0, 2] - dR[2, 0],
                dR[1, 0] - dR[0, 1]
            ]) / (2 * epsilon)

            J[3:, i] = omega

        return J

    @staticmethod
    def rotation_error(R_target, R_current):
        """
        Compute orientation error in axis-angle representation.

        Args:
            R_target, R_current (ndarray): 3x3 rotation matrices

        Returns:
            ndarray: 3D orientation error (axis-angle)
        """
        # Relative rotation
        R_error = R_target @ R_current.T

        # Convert to axis-angle (using scipy)
        rotvec = R.from_matrix(R_error).as_rotvec()

        return rotvec

    def publish_solution(self, q_solution):
        """Publish IK solution as JointState message"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [f'joint_{i+1}' for i in range(self.n_joints)]
        msg.position = q_solution.tolist()

        self.solution_pub.publish(msg)

    @staticmethod
    def pose_stamped_to_transform(msg):
        """Convert PoseStamped to 4x4 homogeneous transform"""
        T = np.eye(4)

        # Position
        T[0, 3] = msg.pose.position.x
        T[1, 3] = msg.pose.position.y
        T[2, 3] = msg.pose.position.z

        # Orientation (quaternion → rotation matrix)
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

    ik_solver = NumericalIKSolver()

    try:
        rclpy.spin(ik_solver)
    except KeyboardInterrupt:
        pass
    finally:
        ik_solver.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
