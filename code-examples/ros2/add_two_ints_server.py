#!/usr/bin/env python3
"""
ROS 2 Service Server Example
Provides a service to add two integers

Usage:
    source /opt/ros/jazzy/setup.bash
    python3 add_two_ints_server.py

    # In another terminal:
    ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 3}"
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):
    """A service server that adds two integers."""

    def __init__(self):
        super().__init__('add_two_ints_server')

        # Create service: service type, service name, callback function
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback
        )

        self.get_logger().info('Add Two Ints Server started!')
        self.get_logger().info('Ready to add integers. Call with: ros2 service call /add_two_ints ...')

    def add_two_ints_callback(self, request, response):
        """
        Called when a client sends a request.

        Args:
            request: AddTwoInts.Request with fields 'a' and 'b'
            response: AddTwoInts.Response with field 'sum'

        Returns:
            response: The populated response object
        """
        response.sum = request.a + request.b
        self.get_logger().info(f'Incoming request: {request.a} + {request.b}')
        self.get_logger().info(f'Sending response: {response.sum}')

        # IMPORTANT: Must return the response object
        return response


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
