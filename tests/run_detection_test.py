#!/usr/bin/env python3
"""
Automated test for face detection.
Opens test page and verifies:
1. All 12 faces are detected
2. No false positives (exactly 12 faces)
3. Bounding boxes are stable for 5 seconds
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

EXPECTED_FACES = 12
TEST_DURATION = 5  # seconds
STABILITY_THRESHOLD = 10  # max pixels movement allowed


def calculate_stability(history):
    """Calculate max movement using spatial matching (not face_id)."""
    if len(history) < 2:
        return 0

    max_movement = 0

    for i in range(1, len(history)):
        prev_positions = list(history[i-1].values())
        curr_positions = list(history[i].values())

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

            # Only count if there was a nearby face (within 100px)
            if min_dist < 100:
                max_movement = max(max_movement, min_dist)

    return max_movement


def run_test():
    print("=" * 60)
    print("AUTOMATED FACE DETECTION TEST")
    print("=" * 60)

    # Start HTTP server
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("\n[1] Starting HTTP server...")
    server = subprocess.Popen(
        ['python3', '-m', 'http.server', '8081', '--bind', '127.0.0.1'],
        cwd=project_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # Open test page in browser
    print("[2] Opening test page in browser...")
    test_url = "http://127.0.0.1:8081/tests/automated_test.html"
    webbrowser.open(test_url)
    time.sleep(2)  # Wait for browser to open and render

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

    # Check face count
    avg_faces = sum(face_counts) / len(face_counts)
    min_faces = min(face_counts)
    max_faces = max(face_counts)

    print(f"\nFace Detection:")
    print(f"  Expected: {EXPECTED_FACES}")
    print(f"  Average detected: {avg_faces:.1f}")
    print(f"  Min detected: {min_faces}")
    print(f"  Max detected: {max_faces}")

    # Check stability
    stability = calculate_stability(position_history)
    print(f"\nStability:")
    print(f"  Max movement: {stability:.1f} pixels")
    print(f"  Threshold: {STABILITY_THRESHOLD} pixels")

    # Determine pass/fail
    print("\n" + "-" * 60)

    tests_passed = 0
    tests_total = 3

    # Test 1: All 12 faces detected
    if min_faces >= EXPECTED_FACES:
        print("✓ PASS: All 12 faces detected")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Only detected {min_faces}/{EXPECTED_FACES} faces")

    # Test 2: No false positives
    if max_faces <= EXPECTED_FACES:
        print("✓ PASS: No false positives")
        tests_passed += 1
    else:
        print(f"✗ FAIL: False positives detected ({max_faces - EXPECTED_FACES} extra)")

    # Test 3: Stable bounding boxes
    if stability <= STABILITY_THRESHOLD:
        print("✓ PASS: Bounding boxes stable")
        tests_passed += 1
    else:
        print(f"✗ FAIL: Bounding boxes unstable ({stability:.1f}px movement)")

    print("-" * 60)
    print(f"\nOVERALL: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n*** ALL TESTS PASSED ***")
        return True
    else:
        print("\n*** TESTS FAILED - NEEDS ADJUSTMENT ***")
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
