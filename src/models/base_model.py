"""Base class for emotion detection models."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np
from ..data.models import EmotionPrediction, FaceRegion


class BaseEmotionModel(ABC):
    """Abstract base class for emotion detection models."""

    def __init__(self, model_name: str, weight: float = 1.0):
        """
        Initialize emotion model.

        Args:
            model_name: Name identifier for the model
            weight: Weight for ensemble voting (default: 1.0)
        """
        self.model_name = model_name
        self.weight = weight
        self.is_initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the model (load weights, etc.).

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def predict_emotion(
        self,
        frame: np.ndarray,
        face_region: FaceRegion
    ) -> Optional[EmotionPrediction]:
        """
        Predict emotion for a detected face.

        Args:
            frame: Full frame image
            face_region: Region containing the face

        Returns:
            EmotionPrediction or None if prediction fails
        """
        pass

    def extract_face(self, frame: np.ndarray, face_region: FaceRegion) -> np.ndarray:
        """
        Extract face region from frame.

        Args:
            frame: Full frame image
            face_region: Region containing the face

        Returns:
            Cropped face image
        """
        x, y, w, h = face_region.to_tuple()
        return frame[y:y+h, x:x+w]

    @abstractmethod
    def get_supported_emotions(self) -> List[str]:
        """
        Get list of emotions this model can detect.

        Returns:
            List of emotion labels
        """
        pass

    def shutdown(self) -> None:
        """Clean up model resources."""
        pass

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
