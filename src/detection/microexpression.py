"""Microexpression detection and analysis."""

from typing import List, Optional, Deque
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

from ..data.models import FaceAnalysis


@dataclass
class EmotionChange:
    """Represents a change in emotion."""
    from_emotion: str
    to_emotion: str
    timestamp: datetime
    confidence: float
    duration_ms: float


class MicroexpressionDetector:
    """Detects brief, involuntary facial expressions (microexpressions)."""

    def __init__(self, window_ms: int = 500):
        """
        Initialize microexpression detector.

        Args:
            window_ms: Time window for detecting microexpressions (milliseconds)
        """
        self.window_ms = window_ms
        self.window_duration = timedelta(milliseconds=window_ms)

        # Track emotion history for each face
        self.face_histories: dict = {}

    def add_analysis(self, face_id: int, analysis: FaceAnalysis) -> List[EmotionChange]:
        """
        Add a face analysis and check for microexpressions.

        Args:
            face_id: Unique ID for the face
            analysis: Face analysis with emotion

        Returns:
            List of detected emotion changes (microexpressions)
        """
        if face_id not in self.face_histories:
            self.face_histories[face_id] = deque()

        history = self.face_histories[face_id]

        # Add current analysis
        history.append(analysis)

        # Remove old entries outside the window
        cutoff_time = analysis.timestamp - self.window_duration
        while history and history[0].timestamp < cutoff_time:
            history.popleft()

        # Detect microexpressions
        return self._detect_changes(face_id)

    def _detect_changes(self, face_id: int) -> List[EmotionChange]:
        """
        Detect emotion changes in the recent history.

        Args:
            face_id: Face ID to analyze

        Returns:
            List of emotion changes
        """
        history = self.face_histories[face_id]

        if len(history) < 2:
            return []

        changes = []

        # Look for rapid emotion changes
        for i in range(1, len(history)):
            prev = history[i - 1]
            curr = history[i]

            # Check if emotion changed
            if prev.emotion != curr.emotion:
                duration_ms = (curr.timestamp - prev.timestamp).total_seconds() * 1000

                # Microexpression is typically very brief (< 500ms)
                # but we track all changes within our window
                changes.append(EmotionChange(
                    from_emotion=prev.emotion,
                    to_emotion=curr.emotion,
                    timestamp=curr.timestamp,
                    confidence=curr.confidence,
                    duration_ms=duration_ms
                ))

        return changes

    def get_emotion_pattern(self, face_id: int) -> List[str]:
        """
        Get recent emotion pattern for a face.

        Args:
            face_id: Face ID

        Returns:
            List of recent emotions in chronological order
        """
        if face_id not in self.face_histories:
            return []

        return [analysis.emotion for analysis in self.face_histories[face_id]]

    def is_microexpression(self, change: EmotionChange, threshold_ms: float = 200) -> bool:
        """
        Determine if an emotion change qualifies as a microexpression.

        Microexpressions are typically:
        - Very brief (40-500ms, peak around 200ms)
        - Involuntary
        - Often contradictory to displayed emotion

        Args:
            change: Emotion change to evaluate
            threshold_ms: Maximum duration for microexpression

        Returns:
            True if this is likely a microexpression
        """
        return change.duration_ms <= threshold_ms

    def clear_face(self, face_id: int) -> None:
        """
        Clear history for a specific face.

        Args:
            face_id: Face ID to clear
        """
        if face_id in self.face_histories:
            del self.face_histories[face_id]

    def clear_all(self) -> None:
        """Clear all face histories."""
        self.face_histories.clear()
