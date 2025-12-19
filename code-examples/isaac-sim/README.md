# Isaac Sim Code Examples

This directory contains practical code examples for Chapter 06: NVIDIA Isaac Platform.

## Prerequisites

### Hardware Requirements
- **NVIDIA RTX GPU** (minimum RTX 2070, recommended RTX 4070 Ti or higher)
- 16 GB RAM minimum (32 GB recommended)
- 50 GB free disk space

### Software Requirements
- **NVIDIA Isaac Sim 2023.1.0 or later**
- **ROS 2 Humble** (for ROS 2 bridge examples)
- **Python 3.10** (comes with Isaac Sim)
- **Ubuntu 22.04** or **Windows 11** (with WSL2 for ROS 2)

## Installation

### 1. Install Isaac Sim

**Option A: Omniverse Launcher (Recommended)**
```bash
# Download from: https://www.nvidia.com/en-us/omniverse/download/
# Install Omniverse Launcher
# Install "Isaac Sim" from the Exchange tab
```

**Option B: pip Installation**
```bash
# Create virtual environment
python3.10 -m venv isaac_env
source isaac_env/bin/activate  # Windows: isaac_env\Scripts\activate

# Install Isaac Sim
pip install isaacsim==2023.1.0 --extra-index-url https://pypi.nvidia.com
```

### 2. Install ROS 2 Humble (for ROS 2 Bridge)

**Ubuntu 22.04:**
```bash
sudo apt update
sudo apt install ros-humble-desktop
source /opt/ros/humble/setup.bash

# Install ROS 2 tools
sudo apt install ros-humble-tf2-tools ros-humble-rviz2
```

**Windows (WSL2):**
Follow ROS 2 Humble installation guide: https://docs.ros.org/en/humble/Installation.html

## Examples

### Example 1: Create Humanoid Scene (`create_humanoid_scene.py`)

Creates a USD scene file with a humanoid robot and physics environment.

**Features:**
- GPU-accelerated physics scene
- URDF import (if URDF file exists)
- Fallback to capsule-based humanoid
- Ground plane and lighting
- Camera setup

**Run:**
```bash
# If installed via Omniverse Launcher
cd code-examples/isaac-sim
~/.local/share/ov/pkg/isaac_sim-*/python.sh create_humanoid_scene.py

# If installed via pip
python create_humanoid_scene.py
```

**Output:**
- `basic-humanoid-scene.usd` - USD scene file that can be opened in Isaac Sim

**Open in Isaac Sim GUI:**
1. Launch Isaac Sim
2. File → Open
3. Navigate to `basic-humanoid-scene.usd`
4. Press PLAY button to start physics simulation

---

### Example 2: ROS 2 Bridge (`ros2_bridge.py`)

Complete ROS 2 integration example with bidirectional communication.

**Features:**
- Publishes joint states to `/joint_states`
- Publishes clock to `/clock`
- Publishes TF tree to `/tf`
- Subscribes to joint commands from `/joint_commands`
- Action Graph setup for real-time communication

**Run:**
```bash
# Terminal 1: Source ROS 2
source /opt/ros/humble/setup.bash

# Terminal 2: Run Isaac Sim with ROS 2 bridge
cd code-examples/isaac-sim
~/.local/share/ov/pkg/isaac_sim-*/python.sh ros2_bridge.py

# Terminal 3: Test ROS 2 topics
ros2 topic list
ros2 topic echo /joint_states
```

**Test Commands:**
```bash
# List all ROS 2 topics
ros2 topic list

# Echo joint states
ros2 topic echo /joint_states

# Visualize TF tree
ros2 run tf2_tools view_frames

# Monitor simulation clock
ros2 topic echo /clock

# Send joint command
ros2 topic pub /joint_commands sensor_msgs/JointState '{
  header: {frame_id: "base_link"},
  name: ["shoulder", "elbow"],
  position: [0.5, -0.5]
}' --once
```

**Visualize in RViz2:**
```bash
rviz2
```
In RViz2:
1. Add → RobotModel
2. Add → TF
3. Fixed Frame: `world`
4. RobotModel Topic: `/joint_states`

---

## File Structure

```
isaac-sim/
├── README.md                      # This file
├── create_humanoid_scene.py       # USD scene creation
├── ros2_bridge.py                 # ROS 2 integration
├── basic-humanoid-scene.usd       # Generated USD file (after running create_humanoid_scene.py)
└── ../urdf/simple_humanoid.urdf   # URDF file (if available)
```

## Troubleshooting

### Error: "CUDA driver version is insufficient"
**Solution:** Update NVIDIA GPU drivers to latest version (535+ for RTX 40 series)

```bash
# Ubuntu
sudo ubuntu-drivers autoinstall
sudo reboot
```

### Error: "ImportError: libpython3.10.so.1.0"
**Solution:** Use Isaac Sim's bundled Python interpreter

```bash
# Don't use system Python, use Isaac Sim's Python
~/.local/share/ov/pkg/isaac_sim-*/python.sh script.py
```

### Error: "ROS 2 topics not appearing"
**Solution:** Ensure ROS 2 environment is sourced before running

```bash
source /opt/ros/humble/setup.bash
echo $ROS_DISTRO  # Should print "humble"
```

### Error: "GPU not found" or "Vulkan not supported"
**Solution:** Isaac Sim requires NVIDIA RTX GPU. AMD/Intel GPUs won't work.

Alternative: Use Ignition Gazebo (Chapter 05) for non-NVIDIA hardware.

### Error: "URDF import failed"
**Solution:** Scripts create fallback simple robots if URDF not found. To use custom URDF:

1. Place URDF file at `../urdf/simple_humanoid.urdf`
2. Ensure all mesh files referenced in URDF exist
3. Use absolute paths or package:// URIs in URDF

## Performance Tips

1. **Enable GPU Physics:** Always use PhysX GPU acceleration
2. **Headless Mode:** For training, use `headless=True` in SimulationApp
3. **Reduce Rendering:** Lower resolution if framerate drops
4. **Batch Simulation:** Use Isaac Gym for parallel environments (covered in Chapter 06 advanced sections)

## Next Steps

After running these examples:

1. **Read Chapter 06:** Full Isaac Sim deep dive at `docs/isaac-platform/index.mdx`
2. **Explore Isaac Gym:** Massively parallel RL training (Chapter 06 advanced)
3. **Isaac ROS:** GPU-accelerated perception packages (Chapter 06 advanced)
4. **VLA Models:** Vision-Language-Action pipeline (Chapter 10)
5. **Voice-to-Action:** End-to-end voice control (Chapter 11)

## Resources

- [Isaac Sim Documentation](https://docs.omniverse.nvidia.com/isaacsim/latest/index.html)
- [Isaac Sim Python API](https://docs.omniverse.nvidia.com/py/isaacsim/index.html)
- [ROS 2 Bridge Tutorial](https://docs.omniverse.nvidia.com/isaacsim/latest/ros2_tutorials/index.html)
- [Isaac Gym Paper](https://arxiv.org/abs/2108.10470)
- [USD Documentation](https://graphics.pixar.com/usd/docs/index.html)

## License

Code examples are released under MIT License (see LICENSE file in repository root).
