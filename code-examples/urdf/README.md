# URDF Model Examples

This directory contains example URDF models for Chapter 04: URDF & Digital Twins.

## Files

- `simple_humanoid.urdf` - Complete 15-link humanoid robot model

## Prerequisites

```bash
# Install URDF tools and rviz2 (ROS 2 Jazzy)
sudo apt install ros-jazzy-urdf-tutorial \
                 ros-jazzy-joint-state-publisher-gui \
                 ros-jazzy-robot-state-publisher \
                 ros-jazzy-rviz2 \
                 ros-jazzy-xacro

# Source ROS 2 environment
source /opt/ros/jazzy/setup.bash
```

## Simple Humanoid Robot

A complete bipedal humanoid model with:
- **15 links**: base_link (pelvis), torso, head, 2 arms (3 segments each), 2 legs (3 segments each), 2 feet
- **14 joints**: waist, neck, 2 shoulders, 2 elbows, 2 wrists, 2 hips, 2 knees, 2 ankles
- **Total height**: ~1.6 meters (standing upright)
- **Total mass**: ~45 kg

### Robot Structure

```
        head
         |
       (neck)
         |
       torso
    /    |    \
(left_  (waist) (right_
shoulder)     shoulder)
   |             |
left_upper_   right_upper_
  arm           arm
   |             |
(left_        (right_
elbow)         elbow)
   |             |
left_         right_
forearm       forearm
   |             |
(left_        (right_
wrist)         wrist)
   |             |
left_hand     right_hand

      base_link
       /     \
   (left_   (right_
    hip)     hip)
      |        |
   left_    right_
   thigh    thigh
      |        |
   (left_  (right_
    knee)    knee)
      |        |
   left_    right_
    shin     shin
      |        |
   (left_  (right_
   ankle)   ankle)
      |        |
   left_    right_
    foot     foot
```

### Visualizing the Humanoid

#### Method 1: Using urdf_tutorial launch file

```bash
cd code-examples/urdf
ros2 launch urdf_tutorial display.launch.py model:=simple_humanoid.urdf
```

**What opens:**
1. **rviz2** window showing the robot
2. **joint_state_publisher_gui** with sliders for all 14 joints

**Try this:**
- Move the `waist` slider → torso rotates
- Move `neck` slider → head turns
- Move `left_shoulder` and `right_shoulder` → arms raise
- Move `left_elbow` and `right_elbow` → arms bend
- Move `left_hip` and `right_hip` → legs move forward/backward
- Move `left_knee` and `right_knee` → legs bend
- Move `left_ankle` and `right_ankle` → feet tilt

#### Method 2: Manual setup (more control)

**Terminal 1: robot_state_publisher**
```bash
cd code-examples/urdf
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args -p robot_description:="$(cat simple_humanoid.urdf)"
```

**Terminal 2: joint_state_publisher_gui**
```bash
ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

**Terminal 3: rviz2**
```bash
ros2 run rviz2 rviz2
```

**Configure rviz2:**
1. Set Fixed Frame to `base_link`
2. Add → RobotModel
3. Add → TF (shows coordinate frames)
4. Add → Axes (shows world origin)

### Validating the URDF

```bash
cd code-examples/urdf

# Check for syntax errors
check_urdf simple_humanoid.urdf

# Expected output:
# robot name is: simple_humanoid
# ---------- Successfully Parsed XML ---------------
# root Link: base_link has 3 child(ren)
#     child(1):  torso
#         child(1):  head
#         child(2):  left_upper_arm
#             child(1):  left_forearm
#                 child(1):  left_hand
#         child(3):  right_upper_arm
#             child(1):  right_forearm
#                 child(1):  right_hand
#     child(2):  left_thigh
#         child(1):  left_shin
#             child(1):  left_foot
#     child(3):  right_thigh
#         child(1):  right_shin
#             child(1):  right_foot
```

### Viewing the TF Tree

```bash
# Start robot_state_publisher and joint_state_publisher (see Method 2 above)

# In a new terminal, generate TF tree
ros2 run tf2_tools view_frames

# Wait 5 seconds, then view the generated PDF
evince frames.pdf  # Linux
open frames.pdf    # macOS
start frames.pdf   # Windows
```

**What you'll see:** A tree diagram showing all 15 links and their parent-child relationships.

### Viewing TF Transforms in Real-Time

```bash
# List all coordinate frames
ros2 run tf2_ros tf2_echo base_link head

# Output updates continuously:
# Translation: [x, y, z]
# Rotation: [x, y, z, w] (quaternion)
```

**Try different frame pairs:**
```bash
# Head position relative to base
ros2 run tf2_ros tf2_echo base_link head

# Left hand position relative to torso
ros2 run tf2_ros tf2_echo torso left_hand

# Right foot position relative to world
ros2 run tf2_ros tf2_echo base_link right_foot
```

### Inspecting Topics

```bash
# List all topics (should see /robot_description, /joint_states, /tf, etc.)
ros2 topic list

# See robot URDF content
ros2 topic echo /robot_description --once

# See current joint angles
ros2 topic echo /joint_states

# See TF transforms
ros2 topic echo /tf
```

### Testing Joint Limits

The humanoid has realistic joint limits:

| Joint | Type | Limits (degrees) | Notes |
|-------|------|------------------|-------|
| waist | revolute | -45° to +45° | Torso rotation |
| neck | revolute | -90° to +90° | Head turning |
| left/right_shoulder | revolute | Full rotation | Shoulder pitch |
| left/right_elbow | revolute | 0° to 150° | Elbow can't hyperextend |
| left/right_wrist | revolute | -90° to +90° | Wrist pitch |
| left/right_hip | revolute | -45° to 135° | Leg swing |
| left/right_knee | revolute | -135° to 0° | Knee bends backward only |
| left/right_ankle | revolute | -45° to +45° | Foot tilt |

**Test:** Try moving joints beyond their limits in the GUI - they should stop at the limit.

## Modifying the URDF

### Change Robot Colors

Edit the `<material>` sections:

```xml
<!-- Make torso red instead of blue -->
<material name="red">
  <color rgba="1 0 0 1"/>  <!-- R G B A -->
</material>

<!-- Then in torso link: -->
<material name="red"/>
```

### Change Link Dimensions

```xml
<!-- Make arms longer (change upper arm length from 0.3m to 0.4m) -->
<link name="left_upper_arm">
  <visual>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>  <!-- was -0.15, now -0.2 -->
    <geometry>
      <cylinder radius="0.04" length="0.4"/>  <!-- was 0.3, now 0.4 -->
    </geometry>
    ...
```

**Important:** When changing link length, also update:
1. `<origin xyz>` to center the geometry
2. `<inertial>` mass and inertia values
3. Child joint `<origin xyz>` to attach at new end position

### Add a Sensor (Fixed Camera)

```xml
<!-- Add after head link -->
<link name="camera">
  <visual>
    <geometry>
      <box size="0.05 0.02 0.02"/>
    </geometry>
    <material name="black">
      <color rgba="0 0 0 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.05 0.02 0.02"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.1"/>
    <inertia ixx="0.00001" ixy="0" ixz="0" iyy="0.00001" iyz="0" izz="0.00001"/>
  </inertial>
</link>

<joint name="camera_mount" type="fixed">
  <parent link="head"/>
  <child link="camera"/>
  <origin xyz="0.12 0 0" rpy="0 0 0"/>  <!-- front of head -->
</joint>
```

### Convert to Xacro (Advanced)

For cleaner code with macros and parameters:

```bash
# Install xacro
sudo apt install ros-jazzy-xacro

# Convert URDF to Xacro format (manual process)
# See Chapter 04, Section 4: Advanced Topics for Xacro tutorial
```

## Common Issues

### Issue 1: "Package 'robot_state_publisher' not found"

```bash
sudo apt install ros-jazzy-robot-state-publisher
```

### Issue 2: Robot appears at origin but looks wrong

**Check:**
- `<origin xyz>` in visual/collision geometry (should center shapes)
- Cylinder length along z-axis (not radius)
- Box size order: x y z (width, depth, height)

### Issue 3: Robot explodes in Gazebo

**Causes:**
- Incorrect inertia values
- Overlapping collision geometries
- Missing damping in joints

**Fix:**
```xml
<!-- Add damping to all joints -->
<dynamics damping="1.0"/>
```

### Issue 4: Joint moves in wrong direction

**Check:**
- `<axis xyz>` direction (x=roll, y=pitch, z=yaw)
- `<origin rpy>` orientation might be rotated

## Next Steps

1. **Modify the humanoid**: Change colors, dimensions, add sensors
2. **Create your own robot**: Use simple_humanoid.urdf as a template
3. **Learn Xacro**: See Chapter 04, Section 4 for cleaner URDF with macros
4. **Simulate in Gazebo**: Add Gazebo plugins for motors and sensors
5. **Control with ROS 2**: Write nodes to command joint positions

## Additional Resources

- **URDF Tutorial**: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/URDF-Main.html
- **URDF XML Spec**: http://wiki.ros.org/urdf/XML
- **TF2 Tutorial**: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Tf2/Tf2-Main.html
- **Xacro Tutorial**: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/Using-Xacro-to-Clean-Up-a-URDF-File.html
