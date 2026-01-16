#!/usr/bin/env python3
"""
Automated test for face detection on Unsplash dataset.
Tests the same requirements as the FER2013 test:
1. All 12 faces are detected
2. No false positives (exactly 12 faces)
3. Consistent detection (same count every frame)
4. Zero bounding box movement (still images should have no movement)
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
STABILITY_THRESHOLD = 0  # For still images, NO movement allowed


def calculate_stability(history):
    """Calculate max movement using spatial matching (not face_id)."""
    if len(history) < 2:
        return 0, 0

    max_movement = 0
    total_movements = 0
    movement_count = 0

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
                total_movements += min_dist
                movement_count += 1

    avg_movement = total_movements / movement_count if movement_count > 0 else 0
    return max_movement, avg_movement


def check_consistency(face_counts):
    """Check if face count is consistent across all frames."""
    if not face_counts:
        return False, 0, 0

    # For still images, we want EXACTLY the same count every frame
    unique_counts = set(face_counts)
    is_consistent = len(unique_counts) == 1
    variance = max(face_counts) - min(face_counts)

    return is_consistent, variance, face_counts[0] if is_consistent else -1


def run_test():
    print("=" * 60)
    print("UNSPLASH DATASET FACE DETECTION TEST")
    print("=" * 60)

    # Start HTTP server
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("\n[1] Starting HTTP server...")
    server = subprocess.Popen(
        ['python3', '-m', 'http.server', '8083', '--bind', '127.0.0.1'],
        cwd=project_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    # Open test page in browser
    print("[2] Opening Unsplash test page in browser...")
    test_url = "http://127.0.0.1:8083/tests/unsplash_test.html"
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
    print(f"  Frames processed: {len(face_counts)}")

    # Check consistency
    is_consistent, variance, consistent_count = check_consistency(face_counts)
    print(f"\nConsistency (still image test):")
    print(f"  Same count every frame: {'Yes' if is_consistent else 'No'}")
    print(f"  Count variance: {variance} (should be 0)")
    print(f"  Unique counts seen: {sorted(set(face_counts))}")

    # Check stability
    max_movement, avg_movement = calculate_stability(position_history)
    print(f"\nBounding Box Stability (still image test):")
    print(f"  Max movement: {max_movement:.1f} pixels (should be 0)")
    print(f"  Avg movement: {avg_movement:.1f} pixels")

    # Determine pass/fail
    print("\n" + "-" * 60)

    tests_passed = 0
    tests_total = 4

    # Test 1: All 12 faces detected
    if min_faces >= EXPECTED_FACES:
        print("PASS: All 12 faces detected in every frame")
        tests_passed += 1
    else:
        print(f"FAIL: Only detected {min_faces}/{EXPECTED_FACES} faces (min across frames)")

    # Test 2: No false positives
    if max_faces <= EXPECTED_FACES:
        print("PASS: No false positives")
        tests_passed += 1
    else:
        print(f"FAIL: False positives detected ({max_faces - EXPECTED_FACES} extra)")

    # Test 3: Consistent detection (same count every frame for still images)
    if is_consistent and consistent_count == EXPECTED_FACES:
        print("PASS: Consistent detection (exactly 12 in every frame)")
        tests_passed += 1
    elif is_consistent:
        print(f"FAIL: Consistent but wrong count ({consistent_count} instead of {EXPECTED_FACES})")
    else:
        print(f"FAIL: Inconsistent detection (count varies: {min_faces}-{max_faces})")

    # Test 4: Zero bounding box movement (still images should have NO movement)
    if max_movement == 0:
        print("PASS: Zero bounding box movement (perfect for still images)")
        tests_passed += 1
    else:
        print(f"FAIL: Bounding boxes moving on still image ({max_movement:.1f}px max)")

    print("-" * 60)
    print(f"\nOVERALL: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n*** ALL UNSPLASH TESTS PASSED ***")
        return True
    else:
        print("\n*** UNSPLASH TESTS NEED ADJUSTMENT ***")
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
