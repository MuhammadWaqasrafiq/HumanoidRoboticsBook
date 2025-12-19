#!/usr/bin/env python3
"""
ROS 2 Action Server Example
Simulates a robot moving to a target with progress feedback

Usage:
    source /opt/ros/jazzy/setup.bash
    python3 move_to_target_server.py

    # In another terminal:
    ros2 action send_goal /move_to_target example_interfaces/action/Fibonacci "{order: 5}" --feedback
"""

import time
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class MoveToTargetServer(Node):
    """
    Action server that simulates moving a robot to a target position.
    Uses Fibonacci action as a placeholder (order = target distance in meters).
    """

    def __init__(self):
        super().__init__('move_to_target_server')

        # Create action server: node, action type, action name, callback
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'move_to_target',
            self.execute_callback
        )

        self.get_logger().info('Move To Target Action Server started!')
        self.get_logger().info('Waiting for action goals...')

    def execute_callback(self, goal_handle):
        """
        Called when a goal is received from an action client.

        Args:
            goal_handle: Handle to control goal lifecycle (feedback, cancel, result)

        Returns:
            result: Fibonacci.Result object with final outcome
        """
        self.get_logger().info('Received goal request')

        # Get goal parameters (using 'order' as target distance)
        target_distance = goal_handle.request.order
        self.get_logger().info(f'Target distance: {target_distance} meters')

        # Initialize feedback message
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = []

        # Simulate movement with periodic feedback
        for i in range(target_distance):
            # Check if goal was canceled by client
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled by client')
                return Fibonacci.Result()

            # Update and publish feedback (progress)
            feedback_msg.sequence.append(i)
            goal_handle.publish_feedback(feedback_msg)

            progress_percent = int((i / target_distance) * 100)
            self.get_logger().info(
                f'Progress: {i}/{target_distance} meters ({progress_percent}%)'
            )

            # Simulate 1 second per meter of movement
            time.sleep(1)

        # Complete the final step
        feedback_msg.sequence.append(target_distance)
        goal_handle.publish_feedback(feedback_msg)

        # Mark goal as succeeded
        goal_handle.succeed()

        # Build result message
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Goal succeeded! Moved {target_distance} meters')

        return result


def main(args=None):
    rclpy.init(args=args)
    node = MoveToTargetServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
