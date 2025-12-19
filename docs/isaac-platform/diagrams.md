# Chapter 06: Additional Mermaid Diagrams

This file contains additional Mermaid diagrams for Chapter 06 that can be integrated into the main content or subsections.

## Diagram 1: URDF to USD Import Pipeline

Shows the complete process of importing a URDF robot into Isaac Sim and converting to USD format.

```mermaid
flowchart TB
    A[URDF File<br/>robot.urdf] --> B{Import Method}
    B -->|GUI Method| C[File → Import → URDF]
    B -->|Python API| D[URDFParseAndImportFile]

    C --> E[URDF Parser]
    D --> E

    E --> F{Parse URDF}
    F -->|Links| G[Create USD Prims]
    F -->|Joints| H[Create Articulation]
    F -->|Meshes| I[Convert to USD Geometry]
    F -->|Physics| J[Add Collision Shapes]

    G --> K[USD Robot Prim]
    H --> K
    I --> K
    J --> K

    K --> L{Configuration}
    L -->|Fix Base?| M[Fixed/Mobile Robot]
    L -->|Self Collision?| N[Enable Collision]
    L -->|Drive Type| O[Position/Velocity/Effort]

    M --> P[Final USD File<br/>robot.usd]
    N --> P
    O --> P

    P --> Q[Simulation Ready]

    style A fill:#e1f5ff
    style P fill:#c8e6c9
    style Q fill:#76b900
    style E fill:#fff9c4
    style K fill:#ffccbc
```

**Use Case:** Include this in the "Importing URDF Humanoid" section to show the complete workflow.

---

## Diagram 2: ROS 2 Bridge Architecture

Illustrates the bidirectional communication between Isaac Sim and ROS 2 ecosystem.

```mermaid
graph TB
    subgraph "Isaac Sim"
        A[Action Graph System]
        B[On Playback Tick<br/>Clock Source]
        C[Robot Articulation<br/>USD Prim]

        D[ROS2 Publishers]
        E[ROS2 Subscribers]

        B --> D
        C --> D
        E --> C
    end

    subgraph "ROS 2 Topics"
        F[/joint_states<br/>sensor_msgs/JointState]
        G[/clock<br/>rosgraph_msgs/Clock]
        H[/tf<br/>tf2_msgs/TFMessage]
        I[/joint_commands<br/>sensor_msgs/JointState]
    end

    subgraph "ROS 2 Nodes"
        J[Robot State Publisher]
        K[Controller Manager]
        L[Custom Control Node]
        M[RViz2 Visualization]
    end

    D -->|Publish| F
    D -->|Publish| G
    D -->|Publish| H
    I -->|Subscribe| E

    F --> J
    G --> M
    H --> M
    L --> I
    K --> I

    J --> N[URDF Transform Tree]
    N --> M

    style A fill:#76b900
    style D fill:#00adef
    style E fill:#ffcc00
    style M fill:#9966ff
```

**Use Case:** Include this in the "ROS 2 Bridge Setup" section to explain the communication flow.

---

## Diagram 3: GPU Physics Pipeline

Shows how PhysX 5 GPU physics works with PyTorch tensor API.

```mermaid
flowchart LR
    subgraph "CPU Side"
        A[Python Script] --> B[Isaac Sim API]
        B --> C[Action Graph]
    end

    subgraph "GPU Side - PhysX 5"
        D[Physics Scene]
        E[Rigid Bodies]
        F[Articulations]
        G[Collision Detection]
        H[Constraint Solver]

        D --> E
        D --> F
        E --> G
        F --> G
        G --> H
    end

    subgraph "Tensor API"
        I[GPU Memory Pool]
        J[State Tensors<br/>positions, velocities]
        K[Force Tensors<br/>joint torques]
        L[PyTorch Tensors<br/>Direct GPU Access]

        I --> J
        I --> K
        J --> L
        K --> L
    end

    C -->|Configure| D
    H -->|Update| J
    L -->|Read/Write| H

    L --> M[RL Training Loop<br/>Parallel Environments]
    M -->|Control Actions| L

    style D fill:#76b900
    style H fill:#ffcc00
    style L fill:#9966ff
    style M fill:#ff6b6b
```

**Use Case:** Include this in the "Key Concepts" section under "PhysX Tensor API for RL Training".

---

## Diagram 4: Synthetic Data Generation Pipeline

Shows Omniverse Replicator workflow for generating training datasets.

```mermaid
flowchart TB
    A[3D Scene Setup<br/>Isaac Sim] --> B[Domain Randomization]

    B --> C{Randomization Types}
    C -->|Lighting| D[Random HDRIs<br/>Random Intensities]
    C -->|Textures| E[Random Materials<br/>Random Colors]
    C -->|Poses| F[Random Joint States<br/>Random Camera Angles]
    C -->|Scene| G[Random Props<br/>Random Backgrounds]

    D --> H[Replicator Script]
    E --> H
    F --> H
    G --> H

    H --> I{Render Loop}

    I -->|RGB Camera| J[RGB Images]
    I -->|Depth Camera| K[Depth Maps]
    I -->|Semantic Seg| L[Pixel Labels]
    I -->|Bounding Box| M[Object Detections]
    I -->|Normal Map| N[Surface Normals]

    J --> O[Annotated Dataset]
    K --> O
    L --> O
    M --> O
    N --> O

    O --> P{Training Pipeline}
    P --> Q[Object Detection Model]
    P --> R[Depth Estimation Model]
    P --> S[Segmentation Model]

    style A fill:#e1f5ff
    style H fill:#76b900
    style O fill:#ffcc00
    style P fill:#9966ff
```

**Use Case:** Include this in a "Synthetic Data Generation" subsection (mentioned as future content in index.mdx).

---

## Diagram 5: Isaac Gym Multi-Environment Training

Illustrates massively parallel RL training with Isaac Gym.

```mermaid
graph TB
    subgraph "Isaac Gym - GPU"
        A[Physics Scene Manager]
        B[Environment 1<br/>Robot Instance]
        C[Environment 2<br/>Robot Instance]
        D[Environment 3<br/>Robot Instance]
        E[...]
        F[Environment N<br/>Robot Instance]

        A --> B
        A --> C
        A --> D
        A --> E
        A --> F
    end

    subgraph "Tensor Observations"
        G[State Tensor<br/>N x Obs Dim]
        H[Reward Tensor<br/>N x 1]
        I[Done Tensor<br/>N x 1]
    end

    B --> G
    C --> G
    D --> G
    E --> G
    F --> G

    B --> H
    C --> H
    D --> H
    E --> H
    F --> H

    B --> I
    C --> I
    D --> I
    E --> I
    F --> I

    subgraph "RL Algorithm (PyTorch)"
        J[Policy Network π]
        K[Value Network V]
        L[PPO Optimizer]
    end

    G --> J
    G --> K
    J --> M[Action Tensor<br/>N x Act Dim]
    H --> L
    I --> L
    K --> L

    M --> B
    M --> C
    M --> D
    M --> E
    M --> F

    L --> N[Updated Policy]
    N --> J

    style A fill:#76b900
    style G fill:#00adef
    style J fill:#ffcc00
    style L fill:#9966ff
```

**Use Case:** Include this in an "Isaac Gym for RL" subsection (mentioned as future content in index.mdx).

---

## Diagram 6: Isaac ROS Perception Pipeline

Shows how Isaac ROS packages accelerate perception tasks on GPU.

```mermaid
flowchart LR
    subgraph "Sensor Inputs"
        A[Camera<br/>RGB Image]
        B[Stereo Camera<br/>Left/Right]
        C[Lidar<br/>Point Cloud]
    end

    subgraph "Isaac ROS Packages (GPU)"
        D[isaac_ros_image_proc<br/>Rectification, Debayer]
        E[isaac_ros_stereo_image_proc<br/>Disparity, Point Cloud]
        F[isaac_ros_dnn_inference<br/>TensorRT]
        G[isaac_ros_object_detection<br/>YOLOv8, DOPE]
        H[isaac_ros_pose_estimation<br/>CenterPose]
    end

    subgraph "Output"
        I[Detected Objects<br/>Bounding Boxes]
        J[Estimated Poses<br/>6-DoF]
        K[Processed Point Cloud]
    end

    A --> D
    D --> F
    F --> G
    G --> I

    B --> E
    E --> K

    A --> H
    H --> J

    I --> L[Robot Control<br/>Navigation/Manipulation]
    J --> L
    K --> L

    style D fill:#76b900
    style E fill:#76b900
    style F fill:#ffcc00
    style G fill:#9966ff
    style H fill:#00adef
    style L fill:#ff6b6b
```

**Use Case:** Include this in an "Isaac ROS Integration" subsection (mentioned as future content in index.mdx).

---

## Integration Instructions

### Diagram Placement Recommendations:

1. **URDF to USD Import Pipeline** → Insert in "Importing URDF Humanoid" section after the code examples
2. **ROS 2 Bridge Architecture** → Insert in "ROS 2 Bridge Setup" section before the code examples
3. **GPU Physics Pipeline** → Insert in "Key Concepts" section under "PhysX Tensor API for RL Training"
4. **Synthetic Data Generation** → Create new subsection "Advanced: Synthetic Data Generation"
5. **Isaac Gym Multi-Environment Training** → Create new subsection "Advanced: Isaac Gym for RL"
6. **Isaac ROS Perception Pipeline** → Create new subsection "Advanced: Isaac ROS Integration"

### Task T073 Status:
- ✅ 2 diagrams already in index.mdx (Isaac Platform Ecosystem, Interface Overview)
- ✅ 6 additional diagrams created in this file
- ✅ **Total: 8 diagrams** (exceeds target of 4-6)

All diagrams use clear visual hierarchy, color coding, and practical use cases relevant to humanoid robotics development.
