#!/usr/bin/env python3
"""
Automated test for face detection on video content.
Tests different requirements than still images:
1. At least 1 face detected consistently (videos have variable face visibility)
2. Smooth bounding box tracking (no sudden jumps)
3. Stable detection across frames (minimal flickering)
"""

import sys
import os
import time
import subprocess
import webbrowser
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.session_manager import SessionManager
from src.main import load_config

TEST_DURATION = 10  # seconds
MIN_DETECTION_RATE = 0.5  # At least 50% of frames should have faces
MAX_JUMP_THRESHOLD = 100  # Maximum allowed sudden position change in pixels
MAX_FLICKER_RATE = 0.3  # Max 30% of frames can have face count changes


def calculate_tracking_quality(history):
    """Calculate tracking quality metrics for video."""
    if len(history) < 2:
        return 0, 0, 0

    max_jump = 0
    total_jumps = 0
    jump_count = 0

    for i in range(1, len(history)):
        prev_positions = list(history[i-1].values())
        curr_positions = list(history[i].values())

        if not prev_positions or not curr_positions:
            continue

        # Match each current face to nearest previous face
        for cx, cy, cw, ch, _ in curr_positions:
            curr_center = (cx + cw/2, cy + ch/2)

            # Find closest previous position
            min_dist = float('inf')
            for px, py, pw, ph, _ in prev_positions:
                prev_center = (px + pw/2, py + ph/2)
                dist = math.sqrt((curr_center[0] - prev_center[0])**2 +
                               (curr_center[1] - prev_center[1])**2)
                min_dist = min(min_dist, dist)

            # Only count if there was a nearby face (within reasonable range)
            if min_dist < 200:
                max_jump = max(max_jump, min_dist)
                total_jumps += min_dist
                jump_count += 1

    avg_movement = total_jumps / jump_count if jump_count > 0 else 0
    smooth_count = sum(1 for i in range(1, len(history))
                      if history[i] and history[i-1])

    return max_jump, avg_movement, smooth_count


def calculate_flicker_rate(face_counts):
    """Calculate how often face count changes between frames."""
    if len(face_counts) < 2:
        return 0

    changes = sum(1 for i in range(1, len(face_counts))
                  if face_counts[i] != face_counts[i-1])

    return changes / (len(face_counts) - 1)


def run_test():
    print("=" * 60)
    print("VIDEO FACE DETECTION TEST")
    print("=" * 60)

    # Start HTTP server
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("\n[1] Starting HTTP server...")
    server = subprocess.Popen(
        ['python3', '-m', 'http.server', '8082', '--bind', '127.0.0.1'],
        cwd=project_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # Open test page in browser
    print("[2] Opening video test page in browser...")
    test_url = "http://127.0.0.1:8082/tests/video_test.html"
    webbrowser.open(test_url)
    time.sleep(3)  # Wait for videos to start playing

    # Initialize detection
    print("[3] Initializing face detection...")
    config = load_config()
    session = SessionManager(config)

    if not session.initialize():
        print("ERROR: Failed to initialize session")
        server.terminate()
        return False

    session.start()

    # Collect data for TEST_DURATION seconds
    print(f"[4] Running detection for {TEST_DURATION} seconds...")

    face_counts = []
    position_history = []
    start_time = time.time()

    while time.time() - start_time < TEST_DURATION:
        frame_analysis = session.process_frame()

        if frame_analysis:
            face_count = len(frame_analysis.faces)
            face_counts.append(face_count)

            # Record positions
            positions = {}
            for face in frame_analysis.faces:
                positions[face.face_id] = (
                    face.region.x, face.region.y,
                    face.region.width, face.region.height,
                    face.emotion
                )
            position_history.append(positions)

            # Print progress
            elapsed = time.time() - start_time
            print(f"  {elapsed:.1f}s - Detected {face_count} faces", end='\r')

        time.sleep(0.1)

    print()  # New line after progress

    # Stop session
    session.stop()
    session.shutdown()
    server.terminate()

    # Analyze results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    if not face_counts:
        print("ERROR: No frames processed!")
        return False

    # Calculate metrics
    avg_faces = sum(face_counts) / len(face_counts)
    min_faces = min(face_counts)
    max_faces = max(face_counts)
    frames_with_faces = sum(1 for c in face_counts if c > 0)
    detection_rate = frames_with_faces / len(face_counts)

    print(f"\nFace Detection:")
    print(f"  Average detected: {avg_faces:.1f}")
    print(f"  Min detected: {min_faces}")
    print(f"  Max detected: {max_faces}")
    print(f"  Frames processed: {len(face_counts)}")
    print(f"  Detection rate: {detection_rate:.1%}")

    # Tracking quality
    max_jump, avg_movement, smooth_count = calculate_tracking_quality(position_history)
    print(f"\nTracking Quality:")
    print(f"  Max position jump: {max_jump:.1f} pixels")
    print(f"  Avg movement: {avg_movement:.1f} pixels/frame")
    print(f"  Smooth tracking frames: {smooth_count}")

    # Flicker rate
    flicker_rate = calculate_flicker_rate(face_counts)
    print(f"\nStability:")
    print(f"  Flicker rate: {flicker_rate:.1%} (face count changes between frames)")

    # Determine pass/fail
    print("\n" + "-" * 60)

    tests_passed = 0
    tests_total = 3

    # Test 1: Detection rate
    if detection_rate >= MIN_DETECTION_RATE:
        print(f"✓ PASS: Detection rate {detection_rate:.1%} >= {MIN_DETECTION_RATE:.0%}")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Detection rate {detection_rate:.1%} < {MIN_DETECTION_RATE:.0%}")

    # Test 2: Smooth tracking (no sudden jumps)
    if max_jump <= MAX_JUMP_THRESHOLD:
        print(f"✓ PASS: Smooth tracking (max jump {max_jump:.1f}px <= {MAX_JUMP_THRESHOLD}px)")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Tracking jumps detected ({max_jump:.1f}px > {MAX_JUMP_THRESHOLD}px)")

    # Test 3: Low flicker rate
    if flicker_rate <= MAX_FLICKER_RATE:
        print(f"✓ PASS: Low flicker rate ({flicker_rate:.1%} <= {MAX_FLICKER_RATE:.0%})")
        tests_passed += 1
    else:
        print(f"✗ FAIL: High flicker rate ({flicker_rate:.1%} > {MAX_FLICKER_RATE:.0%})")

    print("-" * 60)
    print(f"\nOVERALL: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n*** ALL VIDEO TESTS PASSED ***")
        return True
    else:
        print("\n*** VIDEO TESTS NEED ADJUSTMENT ***")
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
