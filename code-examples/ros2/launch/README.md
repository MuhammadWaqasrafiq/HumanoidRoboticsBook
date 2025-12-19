# ROS 2 Launch File Examples

This directory contains example launch files and parameter configurations for Chapter 03, Section 3.

## Files

- `example.launch.py` - Multi-node launch file with arguments, namespaces, and remappings
- `robot_params.yaml` - Parameter file examples for various node configurations

## Prerequisites

```bash
# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash

# Install demo nodes if not already installed
sudo apt install ros-jazzy-demo-nodes-cpp ros-jazzy-demo-nodes-py
```

## Running the Launch File

### Basic Usage

```bash
# Launch with defaults (2 robots, /chatter topic, 2 Hz)
ros2 launch example.launch.py
```

### Custom Arguments

```bash
# Change number of robots (note: current example supports 2 robots)
ros2 launch example.launch.py robot_count:=2

# Change base topic name
ros2 launch example.launch.py base_topic:=/my_custom_topic

# Change publishing rate
ros2 launch example.launch.py publish_rate:=10.0

# Enable verbose mode (launches rqt_graph)
ros2 launch example.launch.py verbose:=true

# Combine multiple arguments
ros2 launch example.launch.py \
  base_topic:=/robot_comms \
  publish_rate:=5.0 \
  verbose:=true
```

### View Launch Arguments

```bash
# See all available arguments
ros2 launch example.launch.py --show-args
```

## Using Parameter Files

### Load parameters from YAML file

```bash
# Start a node with parameter file
ros2 run demo_nodes_cpp talker --ros-args \
  --params-file robot_params.yaml
```

### Runtime Parameter Operations

```bash
# List all parameters for a running node
ros2 param list /robot1/talker

# Get specific parameter value
ros2 param get /robot1/talker publish_rate

# Set parameter at runtime
ros2 param set /robot1/talker publish_rate 10.0

# Dump all parameters to file
ros2 param dump /robot1/talker > current_params.yaml

# Load parameters from file to running node
ros2 param load /robot1/talker robot_params.yaml
```

## Verifying the System

### Check Running Nodes

```bash
# List all nodes
ros2 node list
# Expected output:
# /robot1/listener
# /robot1/talker
# /robot2/listener
# /robot2/talker
```

### Check Topics

```bash
# List all topics
ros2 topic list

# Check topic info
ros2 topic info /robot1/chatter

# Echo messages
ros2 topic echo /robot1/chatter

# Check publishing rate
ros2 topic hz /robot1/chatter
```

### Visualize with RQT

```bash
# Graph visualization (shows node and topic connections)
rqt_graph

# Or launch with verbose mode to auto-start
ros2 launch example.launch.py verbose:=true
```

## Modifying the Launch File

To add more robots or customize behavior:

1. **Add more nodes**: Copy the node definitions and change namespace
2. **Add parameters**: Include parameter dictionaries or YAML files
3. **Add conditionals**: Use `IfCondition` or `UnlessCondition`
4. **Include other launches**: Use `IncludeLaunchDescription`

Example: Adding Robot 3

```python
# Robot 3 - Publisher
nodes.append(
    Node(
        package='demo_nodes_cpp',
        executable='talker',
        name='talker',
        namespace='robot3',
        parameters=[{
            'publish_rate': publish_rate
        }],
        remappings=[
            ('chatter', base_topic)
        ],
        output='screen'
    )
)

# Robot 3 - Subscriber
nodes.append(
    Node(
        package='demo_nodes_py',
        executable='listener',
        name='listener',
        namespace='robot3',
        remappings=[
            ('chatter', base_topic)
        ],
        output='screen'
    )
)
```

## Troubleshooting

### "Package 'demo_nodes_cpp' not found"

Install demo packages:
```bash
sudo apt install ros-jazzy-demo-nodes-cpp ros-jazzy-demo-nodes-py
```

### "Launch file not found"

Make sure you're running from the correct directory or use absolute path:
```bash
ros2 launch /absolute/path/to/example.launch.py
```

### Nodes not communicating

Check that topic names match:
```bash
# See what topics each node is using
ros2 node info /robot1/talker
ros2 node info /robot1/listener
```

### Parameter not loading

Verify YAML syntax:
- Use double underscore: `ros__parameters`
- Correct indentation (2 spaces)
- Node name matches exactly

## Further Reading

- [ROS 2 Launch Documentation](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html)
- [ROS 2 Parameters](https://docs.ros.org/en/jazzy/Concepts/About-ROS-2-Parameters.html)
- [Launch File Architecture](https://design.ros2.org/articles/roslaunch.html)
