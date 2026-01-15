"""Ensemble voting for emotion predictions from multiple models."""

from typing import Dict, List, Optional
import numpy as np
from collections import defaultdict

from ..data.models import EmotionPrediction


class EnsembleVoter:
    """Combines predictions from multiple models using weighted voting."""

    def __init__(self, method: str = "weighted_voting", min_models_required: int = 2):
        """
        Initialize ensemble voter.

        Args:
            method: Voting method ('weighted_voting', 'average', 'max_confidence')
            min_models_required: Minimum number of models needed for prediction
        """
        self.method = method
        self.min_models_required = min_models_required

    def vote(
        self,
        predictions: List[EmotionPrediction],
        model_weights: Optional[Dict[str, float]] = None
    ) -> Optional[EmotionPrediction]:
        """
        Combine multiple predictions into a single prediction.

        Args:
            predictions: List of predictions from different models
            model_weights: Optional custom weights for each model

        Returns:
            Combined EmotionPrediction or None if insufficient predictions
        """
        if len(predictions) < self.min_models_required:
            return None

        if self.method == "weighted_voting":
            return self._weighted_voting(predictions, model_weights)
        elif self.method == "average":
            return self._average_voting(predictions)
        elif self.method == "max_confidence":
            return self._max_confidence(predictions)
        else:
            raise ValueError(f"Unknown voting method: {self.method}")

    def _weighted_voting(
        self,
        predictions: List[EmotionPrediction],
        model_weights: Optional[Dict[str, float]] = None
    ) -> Optional[EmotionPrediction]:
        """
        Weighted voting: combine scores weighted by model weights and confidence.

        Args:
            predictions: List of predictions
            model_weights: Custom weights per model

        Returns:
            Combined prediction
        """
        # Aggregate emotion scores across all predictions
        emotion_scores = defaultdict(float)
        total_weight = 0.0

        for pred in predictions:
            # Get model weight
            if model_weights and pred.model_name in model_weights:
                model_weight = model_weights[pred.model_name]
            else:
                model_weight = 1.0

            # Weight by both model weight and prediction confidence
            effective_weight = model_weight * pred.confidence

            # Add all emotion scores from this prediction
            for emotion, score in pred.all_scores.items():
                emotion_scores[emotion] += score * effective_weight

            total_weight += effective_weight

        # Normalize scores
        if total_weight > 0:
            emotion_scores = {k: v / total_weight for k, v in emotion_scores.items()}

        # Get dominant emotion
        if not emotion_scores:
            return None

        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])

        return EmotionPrediction(
            model_name="Ensemble",
            emotion=dominant_emotion[0],
            confidence=dominant_emotion[1],
            all_scores=dict(emotion_scores)
        )

    def _average_voting(self, predictions: List[EmotionPrediction]) -> Optional[EmotionPrediction]:
        """
        Average voting: simple average of all scores.

        Args:
            predictions: List of predictions

        Returns:
            Combined prediction
        """
        emotion_scores = defaultdict(float)

        for pred in predictions:
            for emotion, score in pred.all_scores.items():
                emotion_scores[emotion] += score

        # Average
        n = len(predictions)
        emotion_scores = {k: v / n for k, v in emotion_scores.items()}

        # Get dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])

        return EmotionPrediction(
            model_name="Ensemble",
            emotion=dominant_emotion[0],
            confidence=dominant_emotion[1],
            all_scores=dict(emotion_scores)
        )

    def _max_confidence(self, predictions: List[EmotionPrediction]) -> Optional[EmotionPrediction]:
        """
        Max confidence: select prediction with highest confidence.

        Args:
            predictions: List of predictions

        Returns:
            Prediction with highest confidence
        """
        if not predictions:
            return None

        max_pred = max(predictions, key=lambda p: p.confidence)

        return EmotionPrediction(
            model_name="Ensemble",
            emotion=max_pred.emotion,
            confidence=max_pred.confidence,
            all_scores=max_pred.all_scores
        )

    def get_agreement_score(self, predictions: List[EmotionPrediction]) -> float:
        """
        Calculate how much models agree on the emotion.

        Args:
            predictions: List of predictions

        Returns:
            Agreement score (0.0 to 1.0)
        """
        if len(predictions) < 2:
            return 1.0

        # Count votes for each emotion
        emotion_votes = defaultdict(int)
        for pred in predictions:
            emotion_votes[pred.emotion] += 1

        # Calculate agreement as ratio of majority vote
        max_votes = max(emotion_votes.values())
        total_votes = len(predictions)

        return max_votes / total_votes
