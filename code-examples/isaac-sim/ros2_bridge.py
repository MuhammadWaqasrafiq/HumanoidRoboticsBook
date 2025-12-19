#!/usr/bin/env python3
"""
Complete ROS 2 Bridge example for Isaac Sim.
Demonstrates bidirectional communication between Isaac Sim and ROS 2.

This script:
1. Imports URDF humanoid into Isaac Sim
2. Sets up ROS 2 publishers (joint states, clock, TF)
3. Sets up ROS 2 subscribers (joint commands)
4. Enables real-time simulation with ROS 2 integration

Requirements:
- NVIDIA Isaac Sim 2023.1.0 or later
- ROS 2 Humble or later
- NVIDIA RTX GPU

ROS 2 Topics Published:
- /joint_states (sensor_msgs/JointState)
- /clock (rosgraph_msgs/Clock)
- /tf (tf2_msgs/TFMessage)

ROS 2 Topics Subscribed:
- /joint_commands (sensor_msgs/JointState)

Test with:
  ros2 topic list
  ros2 topic echo /joint_states
  ros2 run tf2_ros tf2_echo world base_link
"""

from isaacsim import SimulationApp

# Initialize Isaac Sim
simulation_app = SimulationApp({
    "headless": False,
    "width": 1920,
    "height": 1080,
})

import omni.isaac.core.utils.stage as stage_utils
from omni.isaac.core.utils.extensions import enable_extension
from omni.isaac.core.utils.prims import get_prim_at_path
import omni.kit.commands
import omni.graph.core as og
from omni.isaac.core_nodes.scripts.utils import set_targets
from pxr import UsdGeom, Gf
import numpy as np
import carb

print("=" * 80)
print("Isaac Sim + ROS 2 Bridge Integration")
print("=" * 80)

# Enable required extensions
print("\n[1/6] Enabling extensions...")
enable_extension("omni.isaac.ros2_bridge")
enable_extension("omni.importer.urdf")
enable_extension("omni.isaac.core_nodes")
print("✅ Extensions enabled")

# Create a new stage
print("\n[2/6] Creating scene...")
stage = stage_utils.create_new_stage()

# Add ground plane
stage_utils.add_ground_plane(
    stage=stage,
    z_position=0.0,
    size=100.0,
    color=np.array([0.5, 0.5, 0.5]),
)
print("✅ Ground plane added")

# Import URDF humanoid
print("\n[3/6] Importing URDF humanoid...")
urdf_path = "../urdf/simple_humanoid.urdf"

import os
if os.path.exists(urdf_path):
    success, robot_prim_path = omni.kit.commands.execute(
        "URDFParseAndImportFile",
        urdf_path=urdf_path,
        import_config={
            "merge_fixed_joints": False,
            "convex_decomp": False,
            "fix_base": False,
            "self_collision": True,
            "create_physics_scene": True,
            "default_drive_type": "position",
            "default_position_drive_damping": 1000.0,
            "default_position_drive_stiffness": 10000.0,
        },
    )

    if success:
        print(f"✅ Humanoid imported at: {robot_prim_path}")
    else:
        print("❌ URDF import failed")
        simulation_app.close()
        exit(1)
else:
    print(f"⚠️  URDF not found at {urdf_path}")
    print("Creating simple robot for demonstration...")

    # Create a simple articulated robot
    robot_prim_path = "/World/SimpleRobot"

    # Create robot base
    omni.kit.commands.execute(
        "CreatePrimWithDefaultXform",
        prim_type="Cube",
        prim_path=f"{robot_prim_path}/base_link",
        attributes={"size": 0.5},
    )

    # Create revolute joints and links (simplified)
    joint_names = ["shoulder", "elbow", "wrist"]
    for i, joint_name in enumerate(joint_names):
        link_path = f"{robot_prim_path}/link_{i+1}"
        omni.kit.commands.execute(
            "CreatePrimWithDefaultXform",
            prim_type="Cylinder",
            prim_path=link_path,
            attributes={"radius": 0.05, "height": 0.3},
        )

        # Position links
        link_prim = get_prim_at_path(link_path)
        UsdGeom.XformCommonAPI(link_prim).SetTranslate((0, 0, 0.5 + i * 0.35))

    print(f"✅ Simple robot created at: {robot_prim_path}")

# Set up ROS 2 bridge using Action Graph
print("\n[4/6] Setting up ROS 2 publishers...")

# Create Action Graph
keys = og.Controller.Keys

(graph, nodes, _, _) = og.Controller.edit(
    {
        "graph_path": "/ActionGraph",
        "evaluator_name": "execution",
    },
    {
        keys.CREATE_NODES: [
            # Tick source
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),

            # ROS 2 Publishers
            ("PublishJointState", "omni.isaac.ros2_bridge.ROS2PublishJointState"),
            ("PublishClock", "omni.isaac.ros2_bridge.ROS2PublishClock"),
            ("PublishTF", "omni.isaac.ros2_bridge.ROS2PublishTransformTree"),

            # ROS 2 Subscriber for joint commands
            ("SubscribeJointState", "omni.isaac.ros2_bridge.ROS2SubscribeJointState"),
            ("ArticulationController", "omni.isaac.core_nodes.IsaacArticulationController"),
        ],
        keys.CONNECT: [
            # Connect tick to publishers
            ("OnPlaybackTick.outputs:tick", "PublishJointState.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishTF.inputs:execIn"),

            # Connect subscriber to articulation controller
            ("SubscribeJointState.outputs:execOut", "ArticulationController.inputs:execIn"),
            ("SubscribeJointState.outputs:positionCommand", "ArticulationController.inputs:positionCommand"),
            ("SubscribeJointState.outputs:velocityCommand", "ArticulationController.inputs:velocityCommand"),
            ("SubscribeJointState.outputs:effortCommand", "ArticulationController.inputs:effortCommand"),
        ],
        keys.SET_VALUES: [
            # Configure publishers
            ("PublishJointState.inputs:topicName", "/joint_states"),
            ("PublishClock.inputs:topicName", "/clock"),
            ("PublishTF.inputs:topicName", "/tf"),

            # Configure subscriber
            ("SubscribeJointState.inputs:topicName", "/joint_commands"),
        ],
    },
)

print("✅ Action Graph created")

# Set robot target for nodes
print("\n[5/6] Configuring robot targets...")

# Set target for joint state publisher
set_targets(
    prim=og.Controller.node("/ActionGraph/PublishJointState"),
    attribute="inputs:targetPrim",
    target_prim_paths=[robot_prim_path],
)

# Set target for TF publisher
set_targets(
    prim=og.Controller.node("/ActionGraph/PublishTF"),
    attribute="inputs:targetPrims",
    target_prim_paths=[robot_prim_path],
)

# Set target for articulation controller
set_targets(
    prim=og.Controller.node("/ActionGraph/ArticulationController"),
    attribute="inputs:targetPrim",
    target_prim_paths=[robot_prim_path],
)

# Set target for joint command subscriber
set_targets(
    prim=og.Controller.node("/ActionGraph/SubscribeJointState"),
    attribute="inputs:targetPrim",
    target_prim_paths=[robot_prim_path],
)

print("✅ Robot targets configured")

# Add camera for better visualization
camera_path = "/World/Camera"
stage_utils.add_camera(camera_path)
camera_prim = get_prim_at_path(camera_path)
UsdGeom.XformCommonAPI(camera_prim).SetTranslate((3.0, 3.0, 2.0))

# Add lighting
distant_light = UsdGeom.DistantLight.Define(stage, "/World/DistantLight")
distant_light.CreateIntensityAttr().Set(1000.0)
UsdGeom.XformCommonAPI(distant_light).SetRotate((315, 0, 0), UsdGeom.XformCommonAPI.RotationOrderXYZ)

print("\n[6/6] ROS 2 bridge setup complete!")

print("\n" + "=" * 80)
print("ROS 2 INTEGRATION READY")
print("=" * 80)
print("\n📡 Published Topics:")
print("  - /joint_states (sensor_msgs/JointState)")
print("  - /clock (rosgraph_msgs/Clock)")
print("  - /tf (tf2_msgs/TFMessage)")
print("\n📥 Subscribed Topics:")
print("  - /joint_commands (sensor_msgs/JointState)")

print("\n🧪 Test Commands (run in separate terminal):")
print("\n  # List all ROS 2 topics")
print("  ros2 topic list")
print("\n  # Echo joint states")
print("  ros2 topic echo /joint_states")
print("\n  # View TF tree")
print("  ros2 run tf2_tools view_frames")
print("\n  # Monitor clock")
print("  ros2 topic echo /clock")
print("\n  # Send joint command (example)")
print("  ros2 topic pub /joint_commands sensor_msgs/JointState '{")
print("    header: {frame_id: \"base_link\"},")
print("    name: [\"shoulder\", \"elbow\"],")
print("    position: [0.5, -0.5]")
print("  }' --once")

print("\n🎮 Isaac Sim Controls:")
print("  - Press PLAY button to start simulation")
print("  - ROS 2 topics will start publishing")
print("  - Use RViz2 to visualize robot state")
print("  - Send /joint_commands to control robot")

print("\n💡 RViz2 Visualization:")
print("  rviz2")
print("  - Add → RobotModel")
print("  - Add → TF")
print("  - Fixed Frame: world")

print("\n⏸️  Press PLAY to start, close window to exit")
print("=" * 80 + "\n")

# Keep simulation running
while simulation_app.is_running():
    simulation_app.update()

simulation_app.close()
print("\n✅ Isaac Sim closed. ROS 2 bridge terminated.")
