#!/usr/bin/env python3
"""
Simple ROS 2 Subscriber Node
Subscribes to /chatter topic and prints received messages

Usage:
    source /opt/ros/jazzy/setup.bash
    python3 simple_subscriber.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    """A simple subscriber node that receives string messages."""

    def __init__(self):
        super().__init__('simple_subscriber')

        # Create subscriber: topic name, message type, callback function, queue size
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10  # Queue size
        )
        # Prevent unused variable warning
        self.subscription

        self.get_logger().info('Subscriber node started! Listening to /chatter')

    def listener_callback(self, msg):
        """Called when a message is received on the subscribed topic."""
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = SimpleSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
