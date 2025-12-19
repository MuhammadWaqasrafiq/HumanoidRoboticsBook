# Simulation Comparison Examples

This directory contains example configurations for comparing Gazebo and Isaac Sim performance with the same humanoid robot.

## Overview

Use these examples to:
- Spawn the same URDF robot in both Gazebo and Isaac Sim
- Compare physics performance (FPS, RTF)
- Measure sensor realism
- Evaluate ease of use

## Prerequisites

### For Gazebo (Ignition Fortress)

```bash
# Install Ignition Gazebo and ROS 2 bridge
sudo apt update
sudo apt install ignition-fortress \
                 ros-jazzy-ros-gz-bridge \
                 ros-jazzy-ros-gz-sim

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash
```

### For Isaac Sim

**Requirements:**
- NVIDIA GPU (RTX 2070 or better)
- 32+ GB RAM
- Ubuntu 22.04 or Windows 10/11

**Installation:**
1. Download Omniverse Launcher: https://www.nvidia.com/en-us/omniverse/download/
2. Install "Isaac Sim" from the Library
3. Wait for 10+ GB download and shader compilation

## Quick Comparison Test

### Test 1: Spawn Humanoid in Gazebo

```bash
# Terminal 1: Launch Ignition Gazebo with humanoid
cd ../../code-examples/urdf
ign gazebo -v 4

# In Gazebo GUI:
# 1. Click "Insert" tab
# 2. Browse to simple_humanoid.urdf
# 3. Click to place in world

# Terminal 2: Check topics
ros2 topic list
ros2 topic echo /joint_states
```

**Expected Performance (RTX 4070 Ti):**
- **Physics FPS**: 100-200 Hz
- **Render FPS**: 60-120 FPS
- **RTF**: 1.0-1.5x
- **RAM**: 800 MB

### Test 2: Spawn Humanoid in Isaac Sim

```bash
# Launch Isaac Sim
~/.local/share/ov/pkg/isaac_sim-*/isaac-sim.sh

# In Isaac Sim GUI:
# 1. File → Import → URDF
# 2. Browse to code-examples/urdf/simple_humanoid.urdf
# 3. Import settings:
#    - Import as: Articulation
#    - Enable: Self Collision
#    - Enable: Fix Base Link (uncheck for mobile robot)
# 4. Click "Import"
```

**Expected Performance (RTX 4070 Ti, GPU Physics):**
- **Physics FPS**: 500-2000 Hz
- **Render FPS**: 60-240 FPS
- **RTF**: 5-20x
- **RAM**: 3-8 GB
- **VRAM**: 2-6 GB

## Performance Comparison Script

Create a simple test to measure RTF:

### Gazebo Test

```python
#!/usr/bin/env python3
"""
Measure Gazebo physics performance
"""
import rclpy
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
import time

class GazeboRTFMeasure(Node):
    def __init__(self):
        super().__init__('gazebo_rtf_measure')
        self.sub = self.create_subscription(Clock, '/clock', self.clock_cb, 10)
        self.start_sim_time = None
        self.start_real_time = None
        self.measurements = []

    def clock_cb(self, msg):
        sim_time = msg.clock.sec + msg.clock.nanosec * 1e-9

        if self.start_sim_time is None:
            self.start_sim_time = sim_time
            self.start_real_time = time.time()
            return

        # Measure every 5 seconds
        if sim_time - self.start_sim_time >= 5.0:
            real_elapsed = time.time() - self.start_real_time
            sim_elapsed = sim_time - self.start_sim_time
            rtf = sim_elapsed / real_elapsed

            self.get_logger().info(f'RTF: {rtf:.2f}x (sim: {sim_elapsed:.1f}s, real: {real_elapsed:.1f}s)')
            self.measurements.append(rtf)

            # Reset for next measurement
            self.start_sim_time = sim_time
            self.start_real_time = time.time()

def main():
    rclpy.init()
    node = GazeboRTFMeasure()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        avg_rtf = sum(node.measurements) / len(node.measurements) if node.measurements else 0
        print(f'\nAverage RTF: {avg_rtf:.2f}x')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Run:**
```bash
# Terminal 1: Start Gazebo with humanoid
ign gazebo simple_humanoid.urdf

# Terminal 2: Measure RTF
python3 measure_gazebo_rtf.py
```

## Comparison Metrics

| Metric | How to Measure | Gazebo Expected | Isaac Sim Expected |
|--------|---------------|-----------------|-------------------|
| **Physics FPS** | Check simulator GUI stats | 100-200 Hz | 500-2000 Hz |
| **Render FPS** | Check GPU usage / FPS counter | 60-120 FPS | 60-240 FPS |
| **RTF** | Use measurement script above | 1.0-1.5x | 5-20x |
| **Startup time** | Time from launch to ready | 8-15s | 20-40s |
| **RAM usage** | `htop` or Task Manager | 800 MB | 3-8 GB |
| **VRAM usage** | `nvidia-smi` | 200-500 MB | 2-6 GB |

## Sensor Comparison

### Camera Test

**Gazebo:**
```xml
<!-- Add to URDF -->
<gazebo reference="head">
  <sensor name="camera" type="camera">
    <update_rate>30</update_rate>
    <camera>
      <horizontal_fov>1.57</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
      </image>
      <clip>
        <near>0.1</near>
        <far>100</far>
      </clip>
    </camera>
  </sensor>
</gazebo>
```

**Isaac Sim:**
- Add camera via Create → Camera
- Set resolution in Properties panel
- Enable RTX raytracing for photorealistic output

**Compare:**
- **Lighting realism**: Isaac Sim has raytraced shadows
- **Noise model**: Both support Gaussian noise
- **Performance**: Gazebo is faster, Isaac Sim is more realistic

## Which Simulator for Your Project?

### Choose Gazebo (Ignition) if:
- ✅ No NVIDIA GPU available
- ✅ CPU-only setup (laptop, budget desktop)
- ✅ Traditional robotics (navigation, manipulation without ML)
- ✅ Open-source requirement
- ✅ Lightweight deployment

### Choose Isaac Sim if:
- ✅ Have NVIDIA RTX GPU (2070 or better)
- ✅ ML/AI training (vision, RL, imitation learning)
- ✅ Need 10+ parallel robots
- ✅ Photorealistic sensors required
- ✅ Large-scale data generation

## Troubleshooting

### Gazebo Issues

**Problem**: Robot falls through floor

**Fix:**
```xml
<!-- Use DART physics, not ODE -->
<physics name="default_physics" type="dart">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
</physics>
```

**Problem**: Slow performance (RTF under 1.0)

**Fix:**
```bash
# Run headless (no GUI)
ign gazebo -s simple_humanoid.urdf

# Reduce sensor rates in URDF
<update_rate>10</update_rate>  <!-- was 30 -->
```

### Isaac Sim Issues

**Problem**: Out of VRAM (GPU memory)

**Fix:**
- Reduce scene complexity
- Lower texture resolution
- Disable raytracing (use rasterization)

**Problem**: Slow startup (40+ seconds)

**Cause**: Shader compilation on first run
**Solution**: Wait once, subsequent launches are faster (~20s)

## Next Steps

1. **Test both simulators** with the simple humanoid URDF
2. **Measure performance** on your hardware
3. **Choose primary simulator** based on your project needs
4. **Proceed to Chapter 06** to dive deeper into Isaac Platform

## Resources

- **Gazebo Tutorials**: https://gazebosim.org/docs/fortress/tutorials
- **Isaac Sim Manual Import URDF**: https://docs.omniverse.nvidia.com/isaacsim/latest/features/ext_omni_isaac_urdf.html
- **ROS 2 Gazebo Bridge**: https://github.com/gazebosim/ros_gz
- **Isaac ROS**: https://nvidia-isaac-ros.github.io/
