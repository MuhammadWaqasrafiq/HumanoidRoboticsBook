from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='capstone_voice_handler',
            executable='voice_handler_node',
            name='voice_handler',
            output='screen',
        ),
        Node(
            package='capstone_perception',
            executable='perception_node',
            name='perception',
            output='screen',
        ),
        Node(
            package='capstone_world_model',
            executable='world_model_node',
            name='world_model',
            output='screen',
        ),
        Node(
            package='capstone_task_planner',
            executable='task_planner_node',
            name='task_planner',
            output='screen',
        ),
        Node(
            package='capstone_navigation',
            executable='navigation_node',
            name='navigation',
            output='screen',
        ),
        Node(
            package='capstone_manipulation',
            executable='manipulation_node',
            name='manipulation',
            output='screen',
        ),
        Node(
            package='capstone_vla_integration',
            executable='vla_integration_node',
            name='vla_integration',
            output='screen',
        ),
        # Add robot_state_publisher and joint_state_publisher if using a URDF
        # Add rviz2 for visualization
    ])