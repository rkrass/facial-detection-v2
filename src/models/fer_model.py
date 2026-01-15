"""FER (Facial Expression Recognition) model wrapper."""

from typing import Dict, List, Optional
import numpy as np
import cv2
from datetime import datetime

from .base_model import BaseEmotionModel
from ..data.models import EmotionPrediction, FaceRegion


class FERModel(BaseEmotionModel):
    """Emotion detection using FER library."""

    def __init__(self, weight: float = 1.0):
        """
        Initialize FER model.

        Args:
            weight: Weight for ensemble voting
        """
        super().__init__("FER", weight)
        self.detector = None

    def initialize(self) -> bool:
        """Initialize FER model."""
        try:
            from fer import FER
            self.detector = FER(mtcnn=True)  # Use MTCNN for better face detection
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize FER: {e}")
            try:
                # Fallback to default detector
                from fer import FER
                self.detector = FER()
                self.is_initialized = True
                return True
            except Exception as e2:
                print(f"FER fallback also failed: {e2}")
                self.is_initialized = False
                return False

    def predict_emotion(
        self,
        frame: np.ndarray,
        face_region: FaceRegion
    ) -> Optional[EmotionPrediction]:
        """
        Predict emotion using FER.

        Args:
            frame: Full frame image
            face_region: Region containing the face

        Returns:
            EmotionPrediction or None if prediction fails
        """
        if not self.is_initialized:
            return None

        try:
            # Extract face
            face_img = self.extract_face(frame, face_region)

            # Convert to RGB (FER expects RGB)
            if len(face_img.shape) == 3 and face_img.shape[2] == 3:
                face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            else:
                face_rgb = face_img

            # Detect emotions
            result = self.detector.detect_emotions(face_rgb)

            if not result or len(result) == 0:
                return None

            # Get the first (and typically only) face result
            emotions = result[0]['emotions']

            # Find dominant emotion
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])

            return EmotionPrediction(
                model_name=self.model_name,
                emotion=dominant_emotion[0],
                confidence=dominant_emotion[1],
                all_scores=emotions,
                timestamp=datetime.now()
            )

        except Exception as e:
            print(f"FER prediction error: {e}")
            return None

    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotions."""
        return ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
