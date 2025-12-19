#!/usr/bin/env python3
"""
OpenVLA-7B Basic Inference Example
Demonstrates vision-language-action model for robot control

This script shows how to:
1. Load OpenVLA-7B model from Hugging Face
2. Process camera image + natural language command
3. Generate robot action predictions
4. Visualize and interpret outputs

Requirements:
- NVIDIA GPU with 8+ GB VRAM (14 GB for FP16, 7 GB for INT8)
- PyTorch with CUDA support
- transformers, pillow, numpy

Installation:
    pip install torch torchvision transformers accelerate bitsandbytes pillow numpy

Usage:
    python openvla_inference.py

Author: Physical AI & Humanoid Robotics Book
License: MIT
"""

import torch
from transformers import AutoModelForVision2Seq, AutoProcessor, BitsAndBytesConfig
from PIL import Image
import numpy as np
import time
import argparse

def load_model(quantization="fp16"):
    """
    Load OpenVLA-7B model with optional quantization

    Args:
        quantization (str): "fp16", "int8", or "int4"

    Returns:
        model: Loaded OpenVLA model
        processor: Text and image processor
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using device: {device}")

    if not torch.cuda.is_available():
        print("[WARNING] CUDA not available. Running on CPU will be very slow.")

    # Configure quantization
    quant_config = None
    if quantization == "int8":
        quant_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0
        )
        print("[INFO] Using INT8 quantization (7 GB VRAM)")
    elif quantization == "int4":
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        print("[INFO] Using INT4 quantization (3.5 GB VRAM)")
    else:
        print("[INFO] Using FP16 precision (14 GB VRAM)")

    # Load processor
    print("[INFO] Loading processor...")
    processor = AutoProcessor.from_pretrained(
        "openvla/openvla-7b",
        trust_remote_code=True
    )

    # Load model
    print("[INFO] Loading OpenVLA-7B model (this may take a few minutes on first run)...")
    model = AutoModelForVision2Seq.from_pretrained(
        "openvla/openvla-7b",
        quantization_config=quant_config,
        torch_dtype=torch.float16 if quantization == "fp16" else None,
        device_map="auto",
        trust_remote_code=True
    )

    model_size = sum(p.numel() for p in model.parameters()) / 1e9
    print(f"[SUCCESS] Model loaded successfully!")
    print(f"          Parameters: {model_size:.2f}B")
    print(f"          Device: {model.device}")

    return model, processor, device


def run_inference(model, processor, device, image_path, instruction, verbose=True):
    """
    Run VLA inference on image + text command

    Args:
        model: OpenVLA model
        processor: Processor for inputs
        device: CUDA or CPU
        image_path: Path to robot camera image
        instruction: Natural language command
        verbose: Print detailed output

    Returns:
        actions: Numpy array of predicted actions (7-DoF)
    """
    # Load and process image
    try:
        image = Image.open(image_path).convert("RGB")
        if verbose:
            print(f"\n[IMAGE] Loaded: {image_path} ({image.size[0]}x{image.size[1]})")
    except FileNotFoundError:
        print(f"[ERROR] Image not found: {image_path}")
        print("[INFO] Creating dummy image for demonstration...")
        # Create dummy 224x224 RGB image
        image = Image.new("RGB", (224, 224), color=(128, 128, 128))

    if verbose:
        print(f"[COMMAND] '{instruction}'")

    # Prepare inputs
    inputs = processor(
        text=instruction,
        images=image,
        return_tensors="pt"
    ).to(device)

    # Run inference
    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,  # Deterministic for reproducibility
        )

    inference_time = time.time() - start_time

    # Decode actions
    action_str = processor.decode(outputs[0], skip_special_tokens=True)

    try:
        # Parse action string (format: "joint1,joint2,joint3,joint4,joint5,joint6,gripper")
        actions = np.array([float(x.strip()) for x in action_str.split(",")])
    except ValueError:
        print(f"[ERROR] Failed to parse actions: {action_str}")
        return None

    if verbose:
        print(f"\n[ACTIONS] Predicted in {inference_time*1000:.1f}ms ({1/inference_time:.1f} Hz)")
        print(f"          Raw output: {action_str}")
        print(f"\n          Action vector: {actions}")

        if len(actions) >= 7:
            print(f"\n          Joint 1 (shoulder pan):  {actions[0]:+.3f}")
            print(f"          Joint 2 (shoulder lift): {actions[1]:+.3f}")
            print(f"          Joint 3 (elbow):         {actions[2]:+.3f}")
            print(f"          Joint 4 (wrist 1):       {actions[3]:+.3f}")
            print(f"          Joint 5 (wrist 2):       {actions[4]:+.3f}")
            print(f"          Joint 6 (wrist 3):       {actions[5]:+.3f}")
            print(f"          Gripper:                 {actions[6]:+.3f} (0=open, 1=closed)")
        else:
            print(f"[WARNING] Expected 7 actions, got {len(actions)}")

    return actions


def denormalize_actions(normalized_actions, joint_limits):
    """
    Convert normalized actions [-1, 1] to actual joint angles

    Args:
        normalized_actions: np.array of shape (7,) with values in [-1, 1]
        joint_limits: List of (min, max) tuples for each joint

    Returns:
        actual_angles: np.array with actual joint angles in radians
    """
    actual_angles = []

    for norm_action, (min_limit, max_limit) in zip(normalized_actions, joint_limits):
        # Scale from [-1, 1] to [min_limit, max_limit]
        actual_angle = min_limit + (norm_action + 1) * (max_limit - min_limit) / 2
        actual_angles.append(actual_angle)

    return np.array(actual_angles)


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(description="OpenVLA-7B Inference Example")
    parser.add_argument("--image", type=str, default="robot_camera.jpg",
                        help="Path to robot camera image")
    parser.add_argument("--command", type=str, default="pick up the red cup",
                        help="Natural language command")
    parser.add_argument("--quantization", type=str, default="int8",
                        choices=["fp16", "int8", "int4"],
                        help="Model precision (fp16=14GB, int8=7GB, int4=3.5GB)")

    args = parser.parse_args()

    print("=" * 80)
    print("OpenVLA-7B Inference Example")
    print("Vision-Language-Action Model for Robot Control")
    print("=" * 80)

    # Load model
    model, processor, device = load_model(quantization=args.quantization)

    # Run inference
    actions = run_inference(
        model, processor, device,
        image_path=args.image,
        instruction=args.command,
        verbose=True
    )

    if actions is not None:
        # Example joint limits (radians) for UR5-like robot
        joint_limits = [
            (-3.14, 3.14),   # Joint 1: shoulder pan
            (-1.57, 1.57),   # Joint 2: shoulder lift
            (-3.14, 3.14),   # Joint 3: elbow
            (-3.14, 3.14),   # Joint 4: wrist 1
            (-1.57, 1.57),   # Joint 5: wrist 2
            (-3.14, 3.14),   # Joint 6: wrist 3
            (0.0, 1.0),      # Gripper: 0=open, 1=closed
        ]

        # Denormalize actions
        actual_angles = denormalize_actions(actions[:7], joint_limits)

        print("\n[DENORMALIZED] Actual joint angles (radians):")
        for i, angle in enumerate(actual_angles[:6]):
            print(f"                 Joint {i+1}: {angle:+.3f} rad ({np.degrees(angle):+.1f}°)")
        print(f"                 Gripper: {actual_angles[6]:.3f}")

    print("\n" + "=" * 80)
    print("Inference complete!")
    print("=" * 80)

    # Additional example commands
    print("\n[EXAMPLES] Try these commands:")
    example_commands = [
        "pick up the red cup",
        "place the object on the table",
        "grasp the blue block",
        "move the cup to the left",
        "open the gripper",
    ]

    for cmd in example_commands:
        print(f"  python openvla_inference.py --command \"{cmd}\"")


if __name__ == "__main__":
    main()
