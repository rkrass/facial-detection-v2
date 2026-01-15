"""Deception detection using FACS, microexpressions, and emotion patterns."""

from typing import List, Optional, Tuple
import numpy as np

from ..data.models import FaceAnalysis, ActionUnit
from .microexpression import MicroexpressionDetector, EmotionChange


class DeceptionDetector:
    """Analyzes faces for potential deception signals."""

    def __init__(self, config: dict):
        """
        Initialize deception detector.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        deception_config = config.get('deception', {})

        self.enabled = deception_config.get('enabled', True)
        self.confidence_threshold = deception_config.get('confidence_threshold', 0.8)

        # Get suspicious emotion patterns from config
        self.suspicious_patterns = deception_config.get('suspicious_patterns', [
            ["fear", "contempt"],
            ["disgust", "happiness"],
            ["surprise", "anger"]
        ])

        # FACS Action Units associated with deception
        self.deception_aus = config.get('facs', {}).get('deception_aus', [4, 15, 23, 24])

        # Microexpression detector
        window_ms = deception_config.get('microexpression_window_ms', 500)
        self.microexp_detector = MicroexpressionDetector(window_ms=window_ms)

    def analyze_for_deception(
        self,
        face_id: int,
        analysis: FaceAnalysis
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Analyze a face for deception signals.

        Args:
            face_id: Unique ID for this face
            analysis: Face analysis with emotion and AUs

        Returns:
            Tuple of (is_deceptive, confidence, reason)
        """
        if not self.enabled:
            return (False, 0.0, None)

        deception_scores = []
        reasons = []

        # 1. Check FACS Action Units
        au_score, au_reason = self._check_action_units(analysis.action_units)
        if au_score > 0:
            deception_scores.append(au_score)
            reasons.append(au_reason)

        # 2. Check for microexpressions
        emotion_changes = self.microexp_detector.add_analysis(face_id, analysis)
        microexp_score, microexp_reason = self._check_microexpressions(emotion_changes)
        if microexp_score > 0:
            deception_scores.append(microexp_score)
            reasons.append(microexp_reason)

        # 3. Check emotion patterns
        pattern_score, pattern_reason = self._check_emotion_patterns(face_id, analysis)
        if pattern_score > 0:
            deception_scores.append(pattern_score)
            reasons.append(pattern_reason)

        # 4. Check model agreement (low agreement can indicate suppressed emotion)
        if len(analysis.model_predictions) > 1:
            agreement_score, agreement_reason = self._check_model_disagreement(analysis)
            if agreement_score > 0:
                deception_scores.append(agreement_score)
                reasons.append(agreement_reason)

        # Combine scores
        if not deception_scores:
            return (False, 0.0, None)

        # Use maximum score (any strong signal indicates potential deception)
        final_score = max(deception_scores)
        combined_reason = " | ".join(reasons)

        is_deceptive = final_score >= self.confidence_threshold

        return (is_deceptive, final_score, combined_reason if is_deceptive else None)

    def _check_action_units(self, action_units: List[ActionUnit]) -> Tuple[float, str]:
        """
        Check for deception-related Action Units.

        Args:
            action_units: List of detected AUs

        Returns:
            (score, reason) tuple
        """
        if not action_units:
            return (0.0, "")

        # Count how many deception AUs are present
        present_deception_aus = []
        total_intensity = 0.0

        for au in action_units:
            if au.au_number in self.deception_aus and au.present:
                present_deception_aus.append(au.au_number)
                total_intensity += au.intensity

        if not present_deception_aus:
            return (0.0, "")

        # Calculate score based on number and intensity
        count_score = len(present_deception_aus) / len(self.deception_aus)
        intensity_score = total_intensity / len(present_deception_aus)

        score = (count_score + intensity_score) / 2

        reason = f"Deception AUs detected: {present_deception_aus}"

        return (score, reason)

    def _check_microexpressions(
        self,
        emotion_changes: List[EmotionChange]
    ) -> Tuple[float, str]:
        """
        Check for suspicious microexpressions.

        Args:
            emotion_changes: Recent emotion changes

        Returns:
            (score, reason) tuple
        """
        if not emotion_changes:
            return (0.0, "")

        # Look for rapid emotion changes (microexpressions)
        microexpressions = [
            change for change in emotion_changes
            if self.microexp_detector.is_microexpression(change)
        ]

        if not microexpressions:
            return (0.0, "")

        # Microexpressions that contradict current emotion are suspicious
        avg_confidence = np.mean([me.confidence for me in microexpressions])
        score = min(1.0, len(microexpressions) * 0.3 * avg_confidence)

        reason = f"Microexpression detected: {microexpressions[-1].from_emotion} → {microexpressions[-1].to_emotion}"

        return (score, reason)

    def _check_emotion_patterns(self, face_id: int, analysis: FaceAnalysis) -> Tuple[float, str]:
        """
        Check for suspicious emotion patterns.

        Args:
            face_id: Face ID
            analysis: Current face analysis

        Returns:
            (score, reason) tuple
        """
        # Get recent emotion pattern
        pattern = self.microexp_detector.get_emotion_pattern(face_id)

        if len(pattern) < 2:
            return (0.0, "")

        # Check if recent pattern matches any suspicious patterns
        for suspicious in self.suspicious_patterns:
            if len(suspicious) == 2:
                # Check last two emotions
                if len(pattern) >= 2:
                    last_two = [pattern[-2], pattern[-1]]
                    if set(last_two) == set(suspicious):
                        score = 0.7
                        reason = f"Suspicious emotion sequence: {suspicious[0]} → {suspicious[1]}"
                        return (score, reason)

        return (0.0, "")

    def _check_model_disagreement(self, analysis: FaceAnalysis) -> Tuple[float, str]:
        """
        Check if models disagree significantly (may indicate suppressed emotion).

        Args:
            analysis: Face analysis

        Returns:
            (score, reason) tuple
        """
        predictions = analysis.model_predictions

        if len(predictions) < 2:
            return (0.0, "")

        # Count unique emotion predictions
        emotions = [p.emotion for p in predictions]
        unique_emotions = set(emotions)

        # High disagreement can indicate emotional suppression
        disagreement = len(unique_emotions) / len(predictions)

        if disagreement > 0.5:  # More than half the models disagree
            score = disagreement * 0.6  # Moderate weight
            reason = f"Model disagreement ({len(unique_emotions)} different emotions)"
            return (score, reason)

        return (0.0, "")

    def clear_face(self, face_id: int) -> None:
        """Clear history for a specific face."""
        self.microexp_detector.clear_face(face_id)

    def clear_all(self) -> None:
        """Clear all histories."""
        self.microexp_detector.clear_all()
