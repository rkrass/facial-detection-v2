"""Pytest configuration and fixtures."""

import pytest
import numpy as np
import cv2
from pathlib import Path

from src.data.models import FaceRegion, EmotionPrediction


@pytest.fixture
def sample_frame():
    """Create a sample frame for testing."""
    # Create a simple colored frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = [100, 150, 200]  # BGR
    return frame


@pytest.fixture
def sample_face_region():
    """Create a sample face region."""
    return FaceRegion(x=100, y=100, width=200, height=200, confidence=0.95)


@pytest.fixture
def sample_emotion_prediction():
    """Create a sample emotion prediction."""
    return EmotionPrediction(
        model_name="TestModel",
        emotion="happy",
        confidence=0.85,
        all_scores={
            "happy": 0.85,
            "sad": 0.05,
            "angry": 0.03,
            "neutral": 0.07
        }
    )


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return {
        'performance': {
            'initial_fps': 10,
            'min_fps': 5,
            'max_fps': 30,
            'adaptive': True,
            'target_cpu_percent': 70
        },
        'models': {
            'deepface': {'enabled': True, 'weight': 1.0, 'backend': 'opencv'},
            'fer': {'enabled': True, 'weight': 1.0},
            'mediapipe': {'enabled': True, 'weight': 1.0},
            'opencv': {'enabled': True, 'weight': 1.0}
        },
        'facs': {'enabled': False, 'deception_aus': [4, 15, 23, 24]},
        'ensemble': {'method': 'weighted_voting', 'min_models_required': 2},
        'deception': {
            'enabled': True,
            'confidence_threshold': 0.8,
            'microexpression_window_ms': 500
        },
        'screen_capture': {'monitor': 0, 'region': None},
        'logging': {
            'enabled': False,
            'directory': 'test_sessions',
            'format': 'json',
            'encrypt': False
        }
    }


@pytest.fixture
def sample_face_image():
    """Create a sample face image with basic features."""
    # Create a simple face-like image
    face = np.ones((200, 200, 3), dtype=np.uint8) * 200

    # Draw eyes
    cv2.circle(face, (70, 70), 10, (0, 0, 0), -1)
    cv2.circle(face, (130, 70), 10, (0, 0, 0), -1)

    # Draw nose
    cv2.line(face, (100, 70), (100, 120), (100, 100, 100), 2)

    # Draw mouth (smile)
    cv2.ellipse(face, (100, 140), (40, 20), 0, 0, 180, (0, 0, 0), 2)

    return face
