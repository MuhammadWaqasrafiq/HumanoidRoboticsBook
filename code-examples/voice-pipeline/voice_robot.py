#!/usr/bin/env python3
"""
Voice-Controlled Robot - Complete Pipeline
Microphone → Whisper ASR → LLM Parser → VLA Model → ROS 2

Requirements:
    pip install torch transformers openai-whisper pyaudio wave numpy pillow rclpy cv-bridge

Usage:
    python voice_robot.py

Author: Physical AI & Humanoid Robotics Book
License: MIT
"""

import time
import wave
import numpy as np
from PIL import Image
import pyaudio

# Deep learning imports
import torch
import whisper
from transformers import AutoModelForVision2Seq, AutoProcessor, BitsAndBytesConfig

# ROS 2 imports
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Image as ImageMsg
from cv_bridge import CvBridge

class VoiceToActionPipeline(Node):
    """Complete voice-to-action pipeline for robot control"""

    def __init__(self):
        super().__init__('voice_to_action_pipeline')

        self.get_logger().info("=" * 80)
        self.get_logger().info("Voice-to-Action Pipeline Initializing...")
        self.get_logger().info("=" * 80)

        # Stage 1: Audio Capture
        self.get_logger().info("\n[1/4] Initializing audio capture...")
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.channels = 1
        self.chunk = 1024

        # Stage 2: Speech Recognition (Whisper)
        self.get_logger().info("\n[2/4] Loading Whisper ASR (base model)...")
        self.whisper_model = whisper.load_model("base", device="cuda")
        self.get_logger().info("    Whisper loaded on GPU")

        # Stage 3: VLA Model (OpenVLA with INT8)
        self.get_logger().info("\n[3/4] Loading VLA model (OpenVLA-7B INT8)...")
        quant_config = BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=6.0)

        self.vla_processor = AutoProcessor.from_pretrained(
            "openvla/openvla-7b", trust_remote_code=True
        )
        self.vla_model = AutoModelForVision2Seq.from_pretrained(
            "openvla/openvla-7b",
            quantization_config=quant_config,
            device_map="auto",
            trust_remote_code=True
        )
        self.get_logger().info("    VLA model loaded with INT8 quantization")

        # Stage 4: ROS 2 Integration
        self.get_logger().info("\n[4/4] Setting up ROS 2 publishers/subscribers...")
        self.joint_pub = self.create_publisher(JointState, '/joint_commands', 10)
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(
            ImageMsg, '/camera/image_raw', self.image_callback, 10
        )
        self.latest_image = None

        self.get_logger().info("\n" + "=" * 80)
        self.get_logger().info("✅ Pipeline Ready! Press ENTER to record commands.")
        self.get_logger().info("=" * 80 + "\n")

    def image_callback(self, msg):
        """Store latest camera image from robot"""
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        self.latest_image = Image.fromarray(cv_image)

    def record_audio(self, duration=3.0):
        """Record audio from microphone"""
        self.get_logger().info(f"🎤 Recording for {duration} seconds...")

        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        frames = []
        for _ in range(int(self.sample_rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(np.frombuffer(data, dtype=np.int16))

        stream.stop_stream()
        stream.close()

        audio_data = np.concatenate(frames)

        # Save to temporary WAV file
        filename = "temp_command.wav"
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

        self.get_logger().info(f"✅ Recorded {len(audio_data)} samples")
        return filename

    def transcribe_audio(self, audio_file):
        """Transcribe audio to text using Whisper"""
        self.get_logger().info("📝 Transcribing speech...")
        start_time = time.time()

        result = self.whisper_model.transcribe(audio_file, language="en", fp16=True)
        text = result["text"].strip()
        latency = time.time() - start_time

        self.get_logger().info(f"    Text: '{text}'")
        self.get_logger().info(f"    Time: {latency*1000:.0f}ms")

        return text, latency

    def generate_actions(self, image, command_text):
        """Generate robot actions using VLA model"""
        self.get_logger().info("🤖 Generating actions...")
        start_time = time.time()

        inputs = self.vla_processor(
            text=command_text,
            images=image,
            return_tensors="pt"
        ).to(self.vla_model.device)

        with torch.no_grad():
            outputs = self.vla_model.generate(**inputs, max_new_tokens=512, do_sample=False)

        action_str = self.vla_processor.decode(outputs[0], skip_special_tokens=True)
        actions = np.array([float(x.strip()) for x in action_str.split(",")])
        latency = time.time() - start_time

        self.get_logger().info(f"    Actions: {actions}")
        self.get_logger().info(f"    Time: {latency*1000:.0f}ms")

        return actions, latency

    def publish_to_robot(self, actions):
        """Publish joint commands to robot via ROS 2"""
        self.get_logger().info("📡 Publishing to robot...")
        start_time = time.time()

        joint_msg = JointState()
        joint_msg.header.stamp = self.get_clock().now().to_msg()
        joint_msg.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'gripper']
        joint_msg.position = actions.tolist()

        self.joint_pub.publish(joint_msg)
        latency = time.time() - start_time

        self.get_logger().info(f"    Published to /joint_commands")
        self.get_logger().info(f"    Time: {latency*1000:.0f}ms")

        return latency

    def process_voice_command(self, duration=3.0):
        """Complete pipeline: voice → actions"""
        pipeline_start = time.time()

        self.get_logger().info("\n" + "=" * 80)
        self.get_logger().info("Starting Voice-to-Action Pipeline")
        self.get_logger().info("=" * 80)

        # Stage 1: Record audio
        audio_file = self.record_audio(duration=duration)

        # Stage 2: Transcribe
        text, transcribe_latency = self.transcribe_audio(audio_file)

        if not text:
            self.get_logger().warn("⚠️  No speech detected")
            return False

        # Stage 3 & 4: Generate actions
        if self.latest_image is None:
            self.get_logger().warn("⚠️  No camera image available")
            # Use dummy image for testing
            self.latest_image = Image.new("RGB", (224, 224), color=(128, 128, 128))

        actions, vla_latency = self.generate_actions(self.latest_image, text)

        # Stage 5: Publish to robot
        publish_latency = self.publish_to_robot(actions)

        # Total latency
        total_latency = time.time() - pipeline_start

        self.get_logger().info("\n" + "=" * 80)
        self.get_logger().info("✅ PIPELINE COMPLETE")
        self.get_logger().info(f"   Total Latency: {total_latency:.2f}s")
        self.get_logger().info(f"   Breakdown:")
        self.get_logger().info(f"     - Audio Capture: {duration:.2f}s")
        self.get_logger().info(f"     - Speech Recognition: {transcribe_latency:.3f}s")
        self.get_logger().info(f"     - VLA Inference: {vla_latency:.3f}s")
        self.get_logger().info(f"     - ROS 2 Publish: {publish_latency:.3f}s")

        success = total_latency < 3.0
        status = '✅ PASS' if success else '❌ FAIL'
        self.get_logger().info(f"   Target: <3.0s | Actual: {total_latency:.2f}s | {status}")
        self.get_logger().info("=" * 80 + "\n")

        return success

def main(args=None):
    rclpy.init(args=args)

    pipeline = VoiceToActionPipeline()

    try:
        while True:
            input("\nPress ENTER to record voice command (3 seconds) or Ctrl+C to quit...")
            pipeline.process_voice_command(duration=3.0)

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down voice-to-action pipeline...")

    pipeline.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
