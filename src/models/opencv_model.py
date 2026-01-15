"""OpenCV-based emotion detection model."""

from typing import Dict, List, Optional
import numpy as np
import cv2
from datetime import datetime
import os

from .base_model import BaseEmotionModel
from ..data.models import EmotionPrediction, FaceRegion


class OpenCVModel(BaseEmotionModel):
    """
    Emotion detection using OpenCV with optional custom model.

    Can load a pre-trained Keras/TensorFlow model or use OpenCV's built-in
    face recognition with emotion classification.
    """

    def __init__(self, model_path: Optional[str] = None, weight: float = 1.0):
        """
        Initialize OpenCV model.

        Args:
            model_path: Path to pre-trained model (optional)
            weight: Weight for ensemble voting
        """
        super().__init__("OpenCV", weight)
        self.model_path = model_path
        self.model = None
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

    def initialize(self) -> bool:
        """Initialize OpenCV model."""
        try:
            # Try to load custom model if path provided and exists
            if self.model_path and os.path.exists(self.model_path):
                try:
                    import tensorflow as tf
                    self.model = tf.keras.models.load_model(self.model_path)
                    self.is_initialized = True
                    return True
                except Exception as e:
                    print(f"Failed to load custom model from {self.model_path}: {e}")

            # Fallback: Use simple heuristic-based detection
            # This is a lightweight alternative when no model is available
            print("OpenCV model: Using heuristic-based emotion detection")
            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Failed to initialize OpenCV model: {e}")
            self.is_initialized = False
            return False

    def predict_emotion(
        self,
        frame: np.ndarray,
        face_region: FaceRegion
    ) -> Optional[EmotionPrediction]:
        """
        Predict emotion using OpenCV model.

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

            if self.model is not None:
                # Use loaded Keras/TensorFlow model
                emotion_scores = self._predict_with_model(face_img)
            else:
                # Use heuristic-based prediction
                emotion_scores = self._predict_heuristic(face_img)

            # Get dominant emotion
            dominant_idx = np.argmax(list(emotion_scores.values()))
            dominant_emotion = list(emotion_scores.keys())[dominant_idx]
            confidence = emotion_scores[dominant_emotion]

            return EmotionPrediction(
                model_name=self.model_name,
                emotion=dominant_emotion,
                confidence=confidence,
                all_scores=emotion_scores,
                timestamp=datetime.now()
            )

        except Exception as e:
            print(f"OpenCV prediction error: {e}")
            return None

    def _predict_with_model(self, face_img: np.ndarray) -> Dict[str, float]:
        """
        Predict using loaded model.

        Args:
            face_img: Face image

        Returns:
            Dictionary of emotion scores
        """
        # Preprocess image for model
        face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_gray, (48, 48))
        face_normalized = face_resized / 255.0
        face_input = np.expand_dims(face_normalized, axis=0)
        face_input = np.expand_dims(face_input, axis=-1)

        # Predict
        predictions = self.model.predict(face_input, verbose=0)[0]

        # Convert to dictionary
        return {emotion: float(score) for emotion, score in zip(self.emotion_labels, predictions)}

    def _predict_heuristic(self, face_img: np.ndarray) -> Dict[str, float]:
        """
        Simple heuristic-based emotion prediction using image analysis.

        Args:
            face_img: Face image

        Returns:
            Dictionary of emotion scores
        """
        # Convert to grayscale
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

        # Calculate basic image statistics
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)

        # Detect edges (can indicate facial tension)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()

        # Heuristic scoring based on image properties
        scores = {
            'neutral': 0.4,  # Default
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'surprise': 0.0,
            'fear': 0.0,
            'disgust': 0.0
        }

        # Brightness-based heuristics
        if mean_intensity > 140:
            scores['happy'] += 0.3
            scores['surprise'] += 0.2
        elif mean_intensity < 100:
            scores['sad'] += 0.3
            scores['angry'] += 0.2

        # Variance-based heuristics (facial tension)
        if std_intensity > 50:
            scores['angry'] += 0.2
            scores['fear'] += 0.2
        elif std_intensity < 30:
            scores['neutral'] += 0.2

        # Edge density (facial expression intensity)
        if edge_density > 0.15:
            scores['surprise'] += 0.3
            scores['fear'] += 0.2
        elif edge_density < 0.08:
            scores['neutral'] += 0.2

        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotions."""
        return self.emotion_labels
