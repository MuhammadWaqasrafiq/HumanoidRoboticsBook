#!/usr/bin/env python3
"""
Simple ROS 2 Publisher Node
Publishes string messages to /chatter topic at 1 Hz

Usage:
    source /opt/ros/jazzy/setup.bash
    python3 simple_publisher.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    """A simple publisher node that sends counter messages."""

    def __init__(self):
        super().__init__('simple_publisher')

        # Create publisher: topic name, message type, queue size
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # Create timer: period (seconds), callback function
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.counter = 0
        self.get_logger().info('Publisher node started! Publishing to /chatter at 1 Hz')

    def timer_callback(self):
        """Called every timer period to publish a message."""
        msg = String()
        msg.data = f'Hello World: {self.counter}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = SimplePublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
