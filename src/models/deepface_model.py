"""DeepFace model wrapper for emotion detection."""

from typing import Dict, List, Optional
import numpy as np
import cv2
from datetime import datetime

from .base_model import BaseEmotionModel
from ..data.models import EmotionPrediction, FaceRegion


class DeepFaceModel(BaseEmotionModel):
    """Emotion detection using DeepFace library."""

    def __init__(self, backend: str = "opencv", weight: float = 1.0):
        """
        Initialize DeepFace model.

        Args:
            backend: Face detection backend ('opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface')
            weight: Weight for ensemble voting
        """
        super().__init__("DeepFace", weight)
        self.backend = backend
        self.deepface = None

    def initialize(self) -> bool:
        """Initialize DeepFace model."""
        try:
            from deepface import DeepFace
            self.deepface = DeepFace
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize DeepFace: {e}")
            self.is_initialized = False
            return False

    def predict_emotion(
        self,
        frame: np.ndarray,
        face_region: FaceRegion
    ) -> Optional[EmotionPrediction]:
        """
        Predict emotion using DeepFace.

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

            # Ensure face is large enough
            if face_img.shape[0] < 48 or face_img.shape[1] < 48:
                # Resize to minimum size
                face_img = cv2.resize(face_img, (48, 48))

            # Analyze emotion
            result = self.deepface.analyze(
                face_img,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend=self.backend
            )

            # Handle both single result and list results
            if isinstance(result, list):
                result = result[0]

            # Extract emotion scores
            emotion_scores = result['emotion']
            dominant_emotion = result['dominant_emotion']

            # Normalize scores to sum to 1.0
            total = sum(emotion_scores.values())
            if total > 0:
                normalized_scores = {k: v / total for k, v in emotion_scores.items()}
            else:
                normalized_scores = emotion_scores

            confidence = normalized_scores.get(dominant_emotion, 0.0)

            return EmotionPrediction(
                model_name=self.model_name,
                emotion=dominant_emotion,
                confidence=confidence,
                all_scores=normalized_scores,
                timestamp=datetime.now()
            )

        except Exception as e:
            print(f"DeepFace prediction error: {e}")
            return None

    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotions."""
        return ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
