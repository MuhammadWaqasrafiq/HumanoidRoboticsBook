#!/usr/bin/env python3
"""
ROS 2 Action Client Example
Sends a goal to move robot to target and monitors progress

Usage:
    # Start server first in another terminal
    source /opt/ros/jazzy/setup.bash
    python3 move_to_target_server.py

    # Then run client
    python3 move_to_target_client.py
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class MoveToTargetClient(Node):
    """Action client that sends movement goals and monitors progress."""

    def __init__(self):
        super().__init__('move_to_target_client')

        # Create action client: node, action type, action name
        self._action_client = ActionClient(self, Fibonacci, 'move_to_target')

        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()
        self.get_logger().info('Action server available!')

    def send_goal(self, target_distance):
        """
        Send a goal to the action server.

        Args:
            target_distance: Distance in meters to move
        """
        # Build goal message
        goal_msg = Fibonacci.Goal()
        goal_msg.order = target_distance

        self.get_logger().info(f'Sending goal: Move {target_distance} meters')

        # Send goal asynchronously with feedback callback
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # Register callback for when server accepts/rejects goal
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """
        Called when server responds to goal request.

        Args:
            future: Future object containing goal handle
        """
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected by server')
            return

        self.get_logger().info('Goal accepted by server, execution started')

        # Wait for result asynchronously
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """
        Called when action is complete (succeeded, aborted, or canceled).

        Args:
            future: Future object containing action result
        """
        result = future.result().result
        status = future.result().status

        if status == 4:  # SUCCEEDED
            self.get_logger().info(f'Goal succeeded! Final result: {result.sequence}')
        elif status == 5:  # CANCELED
            self.get_logger().info('Goal was canceled')
        elif status == 6:  # ABORTED
            self.get_logger().info('Goal was aborted')
        else:
            self.get_logger().info(f'Goal completed with status: {status}')

        # Shutdown node after receiving result
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        """
        Called when feedback is received from action server.

        Args:
            feedback_msg: Feedback message with progress updates
        """
        feedback = feedback_msg.feedback
        progress = len(feedback.sequence)

        self.get_logger().info(f'Feedback received: {progress} meters traveled')
        self.get_logger().info(f'Path so far: {feedback.sequence}')


def main(args=None):
    rclpy.init(args=args)
    node = MoveToTargetClient()

    # Send goal to move 5 meters
    target = 5
    print(f'\n=== Sending goal: Move {target} meters ===')
    print('Press Ctrl+C to cancel goal\n')

    node.send_goal(target)

    # Spin until result is received or user cancels
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\nGoal canceled by user')


if __name__ == '__main__':
    main()
