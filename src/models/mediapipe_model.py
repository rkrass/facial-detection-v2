"""MediaPipe model wrapper with landmark-based emotion inference."""

from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2
from datetime import datetime
import os

from .base_model import BaseEmotionModel
from ..data.models import EmotionPrediction, FaceRegion


class MediaPipeModel(BaseEmotionModel):
    """
    Emotion detection using MediaPipe facial landmarks.

    Note: MediaPipe doesn't have built-in emotion detection, so we use
    facial geometry and landmark positions to infer emotions heuristically.
    This provides a different perspective from CNN-based models.
    """

    def __init__(self, weight: float = 1.0):
        """
        Initialize MediaPipe model.

        Args:
            weight: Weight for ensemble voting
        """
        super().__init__("MediaPipe", weight)
        self.face_landmarker = None
        self.last_landmarks = None  # Store landmarks for mesh drawing

    def initialize(self) -> bool:
        """Initialize MediaPipe Face Landmarker using new tasks API."""
        try:
            import mediapipe as mp

            # Find model file
            model_paths = [
                os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'face_landmarker.task'),
                os.path.join(os.getcwd(), 'models', 'face_landmarker.task'),
                '/Users/wow/Code/facial-detection/models/face_landmarker.task'
            ]

            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break

            if not model_path:
                print("MediaPipe: face_landmarker.task model not found")
                return False

            # Configure FaceLandmarker with new tasks API
            base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
            options = mp.tasks.vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                output_face_blendshapes=True,  # Get blendshapes for emotion
                output_facial_transformation_matrixes=False
            )

            self.face_landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize MediaPipe: {e}")
            self.is_initialized = False
            return False

    def predict_emotion(
        self,
        frame: np.ndarray,
        face_region: FaceRegion
    ) -> Optional[EmotionPrediction]:
        """
        Predict emotion using MediaPipe landmarks and blendshapes.

        Args:
            frame: Full frame image
            face_region: Region containing the face

        Returns:
            EmotionPrediction or None if prediction fails
        """
        if not self.is_initialized:
            return None

        try:
            import mediapipe as mp

            # Expand face region for better MediaPipe detection (add 50% margin)
            h, w = frame.shape[:2]
            expand = 0.5
            new_x = max(0, int(face_region.x - face_region.width * expand))
            new_y = max(0, int(face_region.y - face_region.height * expand))
            new_w = min(w - new_x, int(face_region.width * (1 + 2 * expand)))
            new_h = min(h - new_y, int(face_region.height * (1 + 2 * expand)))

            # Extract expanded face region
            face_img = frame[new_y:new_y+new_h, new_x:new_x+new_w]

            # Resize if too small (MediaPipe needs at least 128px)
            min_dim = 192
            if face_img.shape[0] < min_dim or face_img.shape[1] < min_dim:
                scale = max(min_dim / face_img.shape[0], min_dim / face_img.shape[1])
                new_size = (int(face_img.shape[1] * scale), int(face_img.shape[0] * scale))
                face_img = cv2.resize(face_img, new_size, interpolation=cv2.INTER_LINEAR)

            # Convert to RGB
            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

            # Create MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=face_rgb)

            # Process face with new API
            results = self.face_landmarker.detect(mp_image)

            if not results.face_landmarks:
                return None

            # Get landmarks and store for mesh drawing
            landmarks = results.face_landmarks[0]
            self.last_landmarks = [(lm.x, lm.y, lm.z) for lm in landmarks]

            # Use blendshapes if available for more accurate emotion detection
            if results.face_blendshapes:
                emotion_scores = self._analyze_blendshapes(results.face_blendshapes[0])
            else:
                # Fallback to landmark-based analysis
                emotion_scores = self._analyze_landmarks_new(landmarks, face_img.shape)

            # Get dominant emotion
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])

            return EmotionPrediction(
                model_name=self.model_name,
                emotion=dominant_emotion[0],
                confidence=dominant_emotion[1],
                all_scores=emotion_scores,
                timestamp=datetime.now()
            )

        except Exception as e:
            print(f"MediaPipe prediction error: {e}")
            return None

    def get_landmarks(self) -> Optional[List[Tuple[float, float, float]]]:
        """Get the last detected landmarks for mesh drawing."""
        return self.last_landmarks

    def _analyze_blendshapes(self, blendshapes) -> Dict[str, float]:
        """
        Analyze MediaPipe blendshapes to infer emotion.

        Blendshapes provide direct measurements of facial expressions
        which map well to emotions.
        """
        # Extract relevant blendshape values
        bs_dict = {bs.category_name: bs.score for bs in blendshapes}

        scores = {
            'neutral': 0.2,
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'surprise': 0.0,
            'fear': 0.0,
            'disgust': 0.0
        }

        # Happy: smile, mouth open
        smile_left = bs_dict.get('mouthSmileLeft', 0)
        smile_right = bs_dict.get('mouthSmileRight', 0)
        scores['happy'] = (smile_left + smile_right) / 2

        # Sad: frown, mouth down
        frown_left = bs_dict.get('mouthFrownLeft', 0)
        frown_right = bs_dict.get('mouthFrownRight', 0)
        brow_down = bs_dict.get('browDownLeft', 0) + bs_dict.get('browDownRight', 0)
        scores['sad'] = (frown_left + frown_right) / 2 + brow_down * 0.3

        # Surprise: eyes wide, eyebrows up, jaw open
        eye_wide = bs_dict.get('eyeWideLeft', 0) + bs_dict.get('eyeWideRight', 0)
        brow_up = bs_dict.get('browOuterUpLeft', 0) + bs_dict.get('browOuterUpRight', 0)
        jaw_open = bs_dict.get('jawOpen', 0)
        scores['surprise'] = (eye_wide / 2 + brow_up / 2 + jaw_open) / 3

        # Angry: brows down, eyes squint
        brow_inner_down = bs_dict.get('browInnerUp', 0)  # Inverse
        eye_squint = bs_dict.get('eyeSquintLeft', 0) + bs_dict.get('eyeSquintRight', 0)
        scores['angry'] = (1 - brow_inner_down) * 0.3 + (brow_down / 2) + (eye_squint / 4)

        # Fear: eyes wide, brows up inner
        brow_inner_up = bs_dict.get('browInnerUp', 0)
        scores['fear'] = (eye_wide / 2 + brow_inner_up) / 2

        # Disgust: nose wrinkle, upper lip raise
        nose_sneer = bs_dict.get('noseSneerLeft', 0) + bs_dict.get('noseSneerRight', 0)
        upper_lip = bs_dict.get('mouthUpperUpLeft', 0) + bs_dict.get('mouthUpperUpRight', 0)
        scores['disgust'] = (nose_sneer / 2 + upper_lip / 2) / 2

        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: min(1.0, v / total) for k, v in scores.items()}

        return scores

    def _analyze_landmarks_new(self, landmarks, face_shape) -> Dict[str, float]:
        """Analyze landmarks using the new API format."""
        h, w = face_shape[:2]

        # Extract key landmark positions from NormalizedLandmark list
        mouth_top = landmarks[13].y
        mouth_bottom = landmarks[14].y
        mouth_left = landmarks[61].x
        mouth_right = landmarks[291].x
        mouth_left_corner = landmarks[61].y
        mouth_right_corner = landmarks[291].y

        left_eye_top = landmarks[159].y
        left_eye_bottom = landmarks[145].y
        right_eye_top = landmarks[386].y
        right_eye_bottom = landmarks[374].y

        left_eyebrow = landmarks[70].y
        right_eyebrow = landmarks[300].y

        # Calculate features
        mouth_openness = abs(mouth_bottom - mouth_top)
        mouth_width = abs(mouth_right - mouth_left)
        mouth_curve = (mouth_left_corner + mouth_right_corner) / 2 - mouth_top

        left_eye_openness = abs(left_eye_bottom - left_eye_top)
        right_eye_openness = abs(right_eye_bottom - right_eye_top)
        eye_openness = (left_eye_openness + right_eye_openness) / 2

        mouth_openness_norm = mouth_openness * h
        eye_openness_norm = eye_openness * h

        scores = {
            'neutral': 0.3,
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'surprise': 0.0,
            'fear': 0.0,
            'disgust': 0.0
        }

        if mouth_curve < 0 and mouth_width > 0.3:
            scores['happy'] += 0.4
        if mouth_openness_norm > 5:
            scores['happy'] += 0.3

        if mouth_curve > 0:
            scores['sad'] += 0.4
        if left_eyebrow > 0.4 and right_eyebrow > 0.4:
            scores['sad'] += 0.3

        if mouth_openness_norm > 10 and eye_openness_norm > 3:
            scores['surprise'] += 0.6

        if left_eyebrow > 0.35 and right_eyebrow > 0.35:
            scores['angry'] += 0.4

        if eye_openness_norm > 4:
            scores['fear'] += 0.3
        if left_eyebrow < 0.3 and right_eyebrow < 0.3:
            scores['fear'] += 0.3

        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def get_supported_emotions(self) -> List[str]:
        """Get list of supported emotions."""
        return ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']

    def shutdown(self) -> None:
        """Clean up MediaPipe resources."""
        if self.face_landmarker:
            self.face_landmarker.close()
