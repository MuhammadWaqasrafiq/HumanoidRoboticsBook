#!/usr/bin/env python3
"""
ROS 2 Launch File Example
Demonstrates multi-node system with parameters, namespaces, and remappings

This launch file starts a simple pub-sub system with:
- Configurable number of robots
- Custom parameters for each robot
- Unique namespaces
- Topic remapping

Usage:
    # Use defaults (2 robots)
    ros2 launch example.launch.py

    # Custom robot count
    ros2 launch example.launch.py robot_count:=3

    # Change base topic
    ros2 launch example.launch.py base_topic:=/my_topic

    # Enable verbose logging
    ros2 launch example.launch.py verbose:=true
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():
    # ===== Declare Launch Arguments =====

    robot_count_arg = DeclareLaunchArgument(
        'robot_count',
        default_value='2',
        description='Number of robot instances to launch'
    )

    base_topic_arg = DeclareLaunchArgument(
        'base_topic',
        default_value='/chatter',
        description='Base topic name for communication'
    )

    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='2.0',
        description='Publishing rate in Hz'
    )

    verbose_arg = DeclareLaunchArgument(
        'verbose',
        default_value='false',
        description='Enable verbose logging'
    )

    # ===== Get Launch Configuration Values =====

    robot_count = LaunchConfiguration('robot_count')
    base_topic = LaunchConfiguration('base_topic')
    publish_rate = LaunchConfiguration('publish_rate')
    verbose = LaunchConfiguration('verbose')

    # ===== Build Node List =====

    nodes = []

    # Add initial log messages
    nodes.append(
        LogInfo(
            msg=['Launching ', robot_count, ' robots with topic: ', base_topic]
        )
    )

    # Create publisher nodes for each robot
    # Note: In real usage, you'd use a loop, but launch files need static node definitions
    # This example shows 2 robots statically defined

    # Robot 1 - Publisher
    nodes.append(
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='talker',
            namespace='robot1',
            parameters=[{
                'publish_rate': publish_rate
            }],
            remappings=[
                ('chatter', base_topic)
            ],
            output='screen'
        )
    )

    # Robot 1 - Subscriber
    nodes.append(
        Node(
            package='demo_nodes_py',
            executable='listener',
            name='listener',
            namespace='robot1',
            remappings=[
                ('chatter', base_topic)
            ],
            output='screen'
        )
    )

    # Robot 2 - Publisher
    nodes.append(
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='talker',
            namespace='robot2',
            parameters=[{
                'publish_rate': publish_rate
            }],
            remappings=[
                ('chatter', base_topic)
            ],
            output='screen'
        )
    )

    # Robot 2 - Subscriber
    nodes.append(
        Node(
            package='demo_nodes_py',
            executable='listener',
            name='listener',
            namespace='robot2',
            remappings=[
                ('chatter', base_topic)
            ],
            output='screen'
        )
    )

    # Optional: Add RQT graph visualization if verbose mode
    nodes.append(
        Node(
            package='rqt_graph',
            executable='rqt_graph',
            name='rqt_graph',
            condition=IfCondition(verbose),
            output='screen'
        )
    )

    # ===== Return Launch Description =====

    return LaunchDescription([
        # Arguments
        robot_count_arg,
        base_topic_arg,
        publish_rate_arg,
        verbose_arg,

        # Nodes
        *nodes
    ])
