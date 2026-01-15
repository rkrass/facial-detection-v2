"""Unit tests for utility functions."""

import pytest
import numpy as np

from src.utils.validators import (
    validate_frame,
    validate_face_region,
    validate_confidence,
    normalize_confidence,
    validate_emotion
)
from src.utils.performance import PerformanceMonitor


class TestValidators:
    """Test validation functions."""

    def test_validate_frame_valid(self, sample_frame):
        """Test frame validation with valid frame."""
        assert validate_frame(sample_frame) is True

    def test_validate_frame_invalid(self):
        """Test frame validation with invalid inputs."""
        assert validate_frame(None) is False
        assert validate_frame([1, 2, 3]) is False
        assert validate_frame(np.array([])) is False

    def test_validate_face_region_valid(self):
        """Test valid face region."""
        assert validate_face_region(10, 10, 100, 100, 640, 480) is True

    def test_validate_face_region_invalid(self):
        """Test invalid face regions."""
        # Negative coordinates
        assert validate_face_region(-10, 10, 100, 100, 640, 480) is False

        # Out of bounds
        assert validate_face_region(600, 10, 100, 100, 640, 480) is False

        # Zero or negative size
        assert validate_face_region(10, 10, 0, 100, 640, 480) is False

    def test_validate_confidence(self):
        """Test confidence validation."""
        assert validate_confidence(0.5) is True
        assert validate_confidence(0.0) is True
        assert validate_confidence(1.0) is True
        assert validate_confidence(-0.1) is False
        assert validate_confidence(1.1) is False

    def test_normalize_confidence(self):
        """Test confidence normalization."""
        assert normalize_confidence(0.5) == 0.5
        assert normalize_confidence(-0.1) == 0.0
        assert normalize_confidence(1.5) == 1.0

    def test_validate_emotion(self):
        """Test emotion validation."""
        valid_emotions = ['happy', 'sad', 'angry']
        assert validate_emotion('happy', valid_emotions) is True
        assert validate_emotion('HAPPY', valid_emotions) is True
        assert validate_emotion('confused', valid_emotions) is False


class TestPerformanceMonitor:
    """Test performance monitoring."""

    def test_initialization(self):
        """Test performance monitor initialization."""
        monitor = PerformanceMonitor(initial_fps=10, min_fps=5, max_fps=30)

        assert monitor.current_fps == 10
        assert monitor.min_fps == 5
        assert monitor.max_fps == 30

    def test_frame_interval(self):
        """Test frame interval calculation."""
        monitor = PerformanceMonitor(initial_fps=10)
        assert monitor.frame_interval == 0.1  # 1/10

    def test_record_frame_time(self):
        """Test recording frame times."""
        monitor = PerformanceMonitor()

        monitor.record_frame_time(0.05)
        monitor.record_frame_time(0.06)

        assert len(monitor.frame_times) == 2

    def test_adapt_frame_rate(self):
        """Test adaptive frame rate adjustment."""
        monitor = PerformanceMonitor(initial_fps=10, min_fps=5, max_fps=30)

        # Simulate slow processing
        for _ in range(10):
            monitor.record_frame_time(0.2)  # 200ms per frame

        new_fps = monitor.adapt_frame_rate()
        assert new_fps <= monitor.current_fps  # Should reduce FPS
