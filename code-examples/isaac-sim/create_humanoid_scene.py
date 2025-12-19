#!/usr/bin/env python3
"""
Create a basic humanoid scene in Isaac Sim with USD format.
This script generates a USD scene file that can be opened in Isaac Sim.

Requirements:
- NVIDIA Isaac Sim 2023.1.0 or later
- NVIDIA RTX GPU

Output:
- basic-humanoid-scene.usd - USD scene file with humanoid robot
"""

from isaacsim import SimulationApp

# Initialize Isaac Sim (headless mode for scene creation)
simulation_app = SimulationApp({
    "headless": False,
    "width": 1280,
    "height": 720,
})

import omni.isaac.core.utils.stage as stage_utils
from omni.isaac.core.utils.extensions import enable_extension
from omni.isaac.core.utils.prims import define_prim, get_prim_at_path
from omni.isaac.core.utils.rotations import euler_angles_to_quat
import omni.kit.commands
from pxr import UsdGeom, Gf, UsdPhysics, PhysxSchema
import numpy as np
import carb

# Enable required extensions
enable_extension("omni.importer.urdf")
enable_extension("omni.isaac.sensor")

# Create a new stage
stage = stage_utils.create_new_stage()

# Set up physics scene
scene = UsdPhysics.Scene.Define(stage, "/physicsScene")
scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
scene.CreateGravityMagnitudeAttr().Set(9.81)

# Enable GPU physics (PhysX)
physx_scene = PhysxSchema.PhysxSceneAPI.Apply(scene.GetPrim())
physx_scene.CreateEnableGPUDynamicsAttr().Set(True)
physx_scene.CreateBroadphaseTypeAttr().Set("GPU")
physx_scene.CreateSolverTypeAttr().Set("TGS")

print("✅ Physics scene created with GPU acceleration")

# Add ground plane
stage_utils.add_ground_plane(
    stage=stage,
    z_position=0.0,
    size=50.0,
    color=np.array([0.5, 0.5, 0.5]),
    physics_material_path="/World/Physics/GroundMaterial",
)

print("✅ Ground plane added")

# Import URDF humanoid robot
# Note: This assumes you have a URDF file. For demonstration, we'll create a simple humanoid
# In production, replace with your actual URDF path

urdf_path = "../urdf/simple_humanoid.urdf"

# Check if URDF exists, if not, create a simple capsule-based humanoid
import os
if os.path.exists(urdf_path):
    success, robot_prim_path = omni.kit.commands.execute(
        "URDFParseAndImportFile",
        urdf_path=urdf_path,
        import_config={
            "merge_fixed_joints": False,
            "convex_decomp": False,
            "fix_base": False,  # Mobile humanoid
            "self_collision": True,
            "create_physics_scene": False,  # Already created
            "default_drive_type": "position",
            "default_position_drive_damping": 1000.0,
            "default_position_drive_stiffness": 10000.0,
        },
    )

    if success:
        print(f"✅ Humanoid imported from URDF at: {robot_prim_path}")
    else:
        print("❌ URDF import failed")
        robot_prim_path = None
else:
    # Create a simple capsule-based humanoid for demonstration
    print(f"⚠️  URDF not found at {urdf_path}, creating simple capsule humanoid")

    robot_prim_path = "/World/SimpleHumanoid"
    robot_prim = define_prim(robot_prim_path, "Xform")

    # Helper function to create capsule body part
    def create_capsule_part(name, parent_path, radius, height, position, color):
        """Create a capsule-shaped body part with physics"""
        part_path = f"{parent_path}/{name}"

        # Create capsule geometry
        capsule = UsdGeom.Capsule.Define(stage, part_path)
        capsule.CreateRadiusAttr().Set(radius)
        capsule.CreateHeightAttr().Set(height)
        capsule.CreateAxisAttr().Set("Z")

        # Set color
        capsule.CreateDisplayColorAttr().Set([color])

        # Set position
        UsdGeom.XformCommonAPI(capsule).SetTranslate(position)

        # Add collision
        collision_api = UsdPhysics.CollisionAPI.Apply(capsule.GetPrim())

        # Add rigid body (only for root parts)
        if "torso" in name.lower() or "head" in name.lower():
            mass_api = UsdPhysics.MassAPI.Apply(capsule.GetPrim())
            mass_api.CreateMassAttr().Set(1.0)

        return part_path

    # Create body parts (simplified humanoid)
    # Torso
    create_capsule_part(
        "Torso", robot_prim_path,
        radius=0.15, height=0.6,
        position=(0, 0, 1.5),
        color=(0.8, 0.3, 0.3)
    )

    # Head
    create_capsule_part(
        "Head", robot_prim_path,
        radius=0.1, height=0.2,
        position=(0, 0, 2.0),
        color=(0.9, 0.7, 0.6)
    )

    # Arms
    create_capsule_part(
        "LeftUpperArm", robot_prim_path,
        radius=0.05, height=0.3,
        position=(-0.25, 0, 1.65),
        color=(0.8, 0.3, 0.3)
    )

    create_capsule_part(
        "RightUpperArm", robot_prim_path,
        radius=0.05, height=0.3,
        position=(0.25, 0, 1.65),
        color=(0.8, 0.3, 0.3)
    )

    create_capsule_part(
        "LeftLowerArm", robot_prim_path,
        radius=0.04, height=0.3,
        position=(-0.25, 0, 1.25),
        color=(0.9, 0.7, 0.6)
    )

    create_capsule_part(
        "RightLowerArm", robot_prim_path,
        radius=0.04, height=0.3,
        position=(0.25, 0, 1.25),
        color=(0.9, 0.7, 0.6)
    )

    # Legs
    create_capsule_part(
        "LeftUpperLeg", robot_prim_path,
        radius=0.07, height=0.4,
        position=(-0.1, 0, 0.9),
        color=(0.2, 0.2, 0.8)
    )

    create_capsule_part(
        "RightUpperLeg", robot_prim_path,
        radius=0.07, height=0.4,
        position=(0.1, 0, 0.9),
        color=(0.2, 0.2, 0.8)
    )

    create_capsule_part(
        "LeftLowerLeg", robot_prim_path,
        radius=0.06, height=0.4,
        position=(-0.1, 0, 0.4),
        color=(0.2, 0.2, 0.8)
    )

    create_capsule_part(
        "RightLowerLeg", robot_prim_path,
        radius=0.06, height=0.4,
        position=(0.1, 0, 0.4),
        color=(0.2, 0.2, 0.8)
    )

    # Feet
    create_capsule_part(
        "LeftFoot", robot_prim_path,
        radius=0.05, height=0.15,
        position=(-0.1, 0.05, 0.1),
        color=(0.3, 0.3, 0.3)
    )

    create_capsule_part(
        "RightFoot", robot_prim_path,
        radius=0.05, height=0.15,
        position=(0.1, 0.05, 0.1),
        color=(0.3, 0.3, 0.3)
    )

    # Apply articulation root to make it a robot
    articulation_api = UsdPhysics.ArticulationRootAPI.Apply(robot_prim)

    print("✅ Simple capsule humanoid created")

# Add camera for visualization
camera_path = "/World/Camera"
camera = stage_utils.add_camera(camera_path)

# Position camera to view the humanoid
camera_prim = get_prim_at_path(camera_path)
UsdGeom.XformCommonAPI(camera_prim).SetTranslate((3.0, 3.0, 2.0))
UsdGeom.XformCommonAPI(camera_prim).SetRotate((0, 0, 0), UsdGeom.XformCommonAPI.RotationOrderXYZ)

print("✅ Camera added")

# Add lighting
distant_light = UsdGeom.DistantLight.Define(stage, "/World/DistantLight")
distant_light.CreateIntensityAttr().Set(1000.0)
UsdGeom.XformCommonAPI(distant_light).SetRotate((315, 0, 0), UsdGeom.XformCommonAPI.RotationOrderXYZ)

print("✅ Lighting configured")

# Set viewport camera
import omni.kit.viewport.utility as vp_utils
viewport_api = vp_utils.get_active_viewport()
if viewport_api:
    viewport_api.set_active_camera(camera_path)

# Save the scene
output_path = os.path.join(os.path.dirname(__file__), "basic-humanoid-scene.usd")
omni.usd.get_context().save_as_stage(output_path)

print(f"\n✅ Scene saved to: {output_path}")
print("\nScene contents:")
print("  - Physics scene with GPU acceleration")
print("  - Ground plane (50m x 50m)")
print("  - Humanoid robot (URDF or capsule-based)")
print("  - Camera positioned at (3, 3, 2)")
print("  - Distant light for illumination")

print("\n📖 To open this scene:")
print("  1. Launch Isaac Sim")
print("  2. File → Open")
print(f"  3. Navigate to: {output_path}")
print("\n🎮 Controls:")
print("  - Play button: Start physics simulation")
print("  - Mouse drag: Rotate view")
print("  - Mouse wheel: Zoom in/out")
print("  - WASD: Move camera")

# Keep simulation running for preview
print("\n⏸️  Preview mode - close window to exit")
while simulation_app.is_running():
    simulation_app.update()

simulation_app.close()
