"""Unit tests for emotion detection models."""

import pytest
import numpy as np

from src.data.models import FaceRegion, EmotionPrediction
from src.models.ensemble import EnsembleVoter


class TestEnsembleVoter:
    """Test ensemble voting functionality."""

    def test_weighted_voting(self, sample_emotion_prediction):
        """Test weighted voting method."""
        voter = EnsembleVoter(method="weighted_voting", min_models_required=2)

        predictions = [
            EmotionPrediction("Model1", "happy", 0.9, {"happy": 0.9, "sad": 0.1}),
            EmotionPrediction("Model2", "happy", 0.8, {"happy": 0.8, "sad": 0.2}),
            EmotionPrediction("Model3", "sad", 0.7, {"happy": 0.3, "sad": 0.7})
        ]

        result = voter.vote(predictions)

        assert result is not None
        assert result.model_name == "Ensemble"
        assert result.emotion == "happy"  # Majority vote
        assert 0 <= result.confidence <= 1

    def test_min_models_required(self):
        """Test minimum models requirement."""
        voter = EnsembleVoter(method="weighted_voting", min_models_required=2)

        # Only one prediction
        predictions = [
            EmotionPrediction("Model1", "happy", 0.9, {"happy": 0.9, "sad": 0.1})
        ]

        result = voter.vote(predictions)
        assert result is None  # Not enough predictions

    def test_agreement_score(self):
        """Test agreement score calculation."""
        voter = EnsembleVoter()

        # All agree
        predictions = [
            EmotionPrediction("Model1", "happy", 0.9, {}),
            EmotionPrediction("Model2", "happy", 0.8, {}),
            EmotionPrediction("Model3", "happy", 0.85, {})
        ]

        score = voter.get_agreement_score(predictions)
        assert score == 1.0

        # 2 out of 3 agree
        predictions[2] = EmotionPrediction("Model3", "sad", 0.7, {})
        score = voter.get_agreement_score(predictions)
        assert score == pytest.approx(2/3)


class TestFaceRegion:
    """Test FaceRegion data model."""

    def test_to_tuple(self, sample_face_region):
        """Test conversion to tuple."""
        result = sample_face_region.to_tuple()
        assert result == (100, 100, 200, 200)

    def test_center(self, sample_face_region):
        """Test center point calculation."""
        center = sample_face_region.center()
        assert center == (200, 200)  # (100 + 200/2, 100 + 200/2)
