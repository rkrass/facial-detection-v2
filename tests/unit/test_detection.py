"""Unit tests for detection modules."""

import pytest
from datetime import datetime

from src.detection.microexpression import MicroexpressionDetector, EmotionChange
from src.detection.deception import DeceptionDetector
from src.data.models import FaceAnalysis, FaceRegion, ActionUnit


class TestMicroexpressionDetector:
    """Test microexpression detection."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = MicroexpressionDetector(window_ms=500)
        assert detector.window_ms == 500

    def test_emotion_change_detection(self, sample_face_region):
        """Test detection of emotion changes."""
        detector = MicroexpressionDetector(window_ms=500)

        # Create first analysis
        analysis1 = FaceAnalysis(
            face_id=0,
            region=sample_face_region,
            emotion="happy",
            confidence=0.9
        )

        # Create second analysis with different emotion
        analysis2 = FaceAnalysis(
            face_id=0,
            region=sample_face_region,
            emotion="sad",
            confidence=0.85
        )

        # Add analyses
        changes1 = detector.add_analysis(0, analysis1)
        changes2 = detector.add_analysis(0, analysis2)

        assert len(changes1) == 0  # First analysis has no changes
        assert len(changes2) == 1  # Second analysis detected a change
        assert changes2[0].from_emotion == "happy"
        assert changes2[0].to_emotion == "sad"

    def test_is_microexpression(self):
        """Test microexpression classification."""
        detector = MicroexpressionDetector()

        # Very brief change (microexpression)
        change1 = EmotionChange(
            from_emotion="happy",
            to_emotion="fear",
            timestamp=datetime.now(),
            confidence=0.8,
            duration_ms=150
        )

        assert detector.is_microexpression(change1, threshold_ms=200) is True

        # Longer change (not a microexpression)
        change2 = EmotionChange(
            from_emotion="happy",
            to_emotion="sad",
            timestamp=datetime.now(),
            confidence=0.8,
            duration_ms=500
        )

        assert detector.is_microexpression(change2, threshold_ms=200) is False


class TestDeceptionDetector:
    """Test deception detection."""

    def test_initialization(self, test_config):
        """Test detector initialization."""
        detector = DeceptionDetector(test_config)
        assert detector.enabled is True
        assert detector.confidence_threshold == 0.8

    def test_deception_aus_detection(self, test_config, sample_face_region):
        """Test Action Unit based deception detection."""
        detector = DeceptionDetector(test_config)

        # Create analysis with deception AUs
        action_units = [
            ActionUnit(au_number=4, intensity=0.8, present=True),   # Brow Lowerer
            ActionUnit(au_number=15, intensity=0.7, present=True),  # Lip Corner Depressor
        ]

        analysis = FaceAnalysis(
            face_id=0,
            region=sample_face_region,
            emotion="happy",
            confidence=0.9,
            action_units=action_units
        )

        is_deceptive, confidence, reason = detector.analyze_for_deception(0, analysis)

        # Should detect some level of deception
        assert confidence > 0.0
        if is_deceptive:
            assert "AU" in reason or "Deception" in reason
