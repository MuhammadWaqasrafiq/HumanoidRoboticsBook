#!/usr/bin/env python3
"""
ROS 2 Service Client Example
Calls a service to add two integers

Usage:
    # Start server first in another terminal
    source /opt/ros/jazzy/setup.bash
    python3 add_two_ints_server.py

    # Then run client
    python3 add_two_ints_client.py 5 3
"""

import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):
    """A service client that requests addition of two integers."""

    def __init__(self):
        super().__init__('add_two_ints_client')

        # Create client: service type, service name
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

        # Wait for service to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

        self.get_logger().info('Connected to add_two_ints service!')

    def send_request(self, a, b):
        """
        Send a service request and wait for response.

        Args:
            a: First integer
            b: Second integer

        Returns:
            sum: Result of a + b, or None if service call failed
        """
        # Build request message
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        self.get_logger().info(f'Sending request: {a} + {b}')

        # Call service (asynchronous but blocks until response)
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            self.get_logger().info(f'Result: {a} + {b} = {response.sum}')
            return response.sum
        else:
            self.get_logger().error('Service call failed!')
            return None


def main(args=None):
    rclpy.init(args=args)

    # Check command line arguments
    if len(sys.argv) != 3:
        print('Usage: python3 add_two_ints_client.py <a> <b>')
        print('Example: python3 add_two_ints_client.py 5 3')
        return

    # Parse arguments
    try:
        a = int(sys.argv[1])
        b = int(sys.argv[2])
    except ValueError:
        print('Error: Both arguments must be integers')
        return

    # Create client node
    node = AddTwoIntsClient()

    # Send request
    result = node.send_request(a, b)

    if result is not None:
        print(f'\nFinal result: {a} + {b} = {result}')
    else:
        print('\nService call failed')

    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
