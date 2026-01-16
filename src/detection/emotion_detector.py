"""Emotion detection coordination using multiple models."""

from typing import List, Optional, Dict
import numpy as np

from ..data.models import FaceRegion, EmotionPrediction, FaceAnalysis
from ..models import (
    BaseEmotionModel,
    DeepFaceModel,
    FERModel,
    MediaPipeModel,
    OpenCVModel,
    EnsembleVoter,
    FACSAnalyzer
)


class EmotionDetector:
    """Coordinates multiple emotion detection models and combines results."""

    def __init__(self, config: dict):
        """
        Initialize emotion detector with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.models: List[BaseEmotionModel] = []
        self.ensemble = EnsembleVoter(
            method=config.get('ensemble', {}).get('method', 'weighted_voting'),
            min_models_required=config.get('ensemble', {}).get('min_models_required', 2)
        )
        self.facs_analyzer = FACSAnalyzer() if config.get('facs', {}).get('enabled', True) else None
        self.is_initialized = False

    def initialize(self) -> bool:
        """Initialize all enabled emotion models."""
        try:
            models_config = self.config.get('models', {})

            # Initialize DeepFace
            if models_config.get('deepface', {}).get('enabled', True):
                model = DeepFaceModel(
                    backend=models_config['deepface'].get('backend', 'opencv'),
                    weight=models_config['deepface'].get('weight', 1.0)
                )
                if model.initialize():
                    self.models.append(model)
                    print("✓ DeepFace model initialized")

            # Initialize FER
            if models_config.get('fer', {}).get('enabled', True):
                model = FERModel(
                    weight=models_config['fer'].get('weight', 1.0)
                )
                if model.initialize():
                    self.models.append(model)
                    print("✓ FER model initialized")

            # Initialize MediaPipe
            if models_config.get('mediapipe', {}).get('enabled', True):
                model = MediaPipeModel(
                    weight=models_config['mediapipe'].get('weight', 1.0)
                )
                if model.initialize():
                    self.models.append(model)
                    print("✓ MediaPipe model initialized")

            # Initialize OpenCV
            if models_config.get('opencv', {}).get('enabled', True):
                model = OpenCVModel(
                    model_path=models_config['opencv'].get('model_path'),
                    weight=models_config['opencv'].get('weight', 1.0)
                )
                if model.initialize():
                    self.models.append(model)
                    print("✓ OpenCV model initialized")

            # Initialize FACS analyzer
            if self.facs_analyzer:
                if self.facs_analyzer.initialize():
                    print("✓ FACS analyzer initialized")
                else:
                    print("⚠ FACS analyzer initialization failed, continuing without it")

            if len(self.models) == 0:
                print("ERROR: No emotion models were initialized!")
                return False

            print(f"✓ Initialized {len(self.models)} emotion detection models")
            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Failed to initialize emotion detector: {e}")
            self.is_initialized = False
            return False

    def analyze_face(
        self,
        frame: np.ndarray,
        face_region: FaceRegion,
        face_id: int
    ) -> Optional[FaceAnalysis]:
        """
        Analyze a face using all models.

        Args:
            frame: Full frame image
            face_region: Face region to analyze
            face_id: Unique ID for this face

        Returns:
            FaceAnalysis or None if analysis fails
        """
        if not self.is_initialized:
            return None

        # Get predictions from all models
        predictions: List[EmotionPrediction] = []

        for model in self.models:
            try:
                prediction = model.predict_emotion(frame, face_region)
                if prediction:
                    predictions.append(prediction)
            except Exception as e:
                print(f"Error in {model.model_name}: {e}")

        if not predictions:
            return None

        # Get model weights
        model_weights = self._get_model_weights()

        # Combine predictions using ensemble
        ensemble_prediction = self.ensemble.vote(predictions, model_weights)

        if not ensemble_prediction:
            return None

        # Detect Action Units if FACS is enabled
        action_units = []
        if self.facs_analyzer and self.facs_analyzer.is_initialized:
            try:
                action_units = self.facs_analyzer.detect_action_units(frame, face_region)
            except Exception as e:
                print(f"FACS analysis error: {e}")

        # Get landmarks from MediaPipe model if available
        landmarks = None
        for model in self.models:
            if model.model_name == "MediaPipe" and hasattr(model, 'get_landmarks'):
                landmarks_data = model.get_landmarks()
                if landmarks_data and len(landmarks_data) >= 468:
                    # Convert to numpy array for overlay (keep x, y only)
                    import numpy as np
                    landmarks = np.array([(lm[0], lm[1]) for lm in landmarks_data])
                break

        # Create face analysis
        analysis = FaceAnalysis(
            face_id=face_id,
            region=face_region,
            emotion=ensemble_prediction.emotion,
            confidence=ensemble_prediction.confidence,
            model_predictions=predictions,
            action_units=action_units,
            landmarks=landmarks
        )

        return analysis

    def _get_model_weights(self) -> Dict[str, float]:
        """Get model weights from configuration."""
        models_config = self.config.get('models', {})
        weights = {}

        for model_name in ['deepface', 'fer', 'mediapipe', 'opencv']:
            if model_name in models_config:
                weight = models_config[model_name].get('weight', 1.0)
                # Capitalize model names to match model_name in EmotionPrediction
                weights[model_name.replace('deepface', 'DeepFace').replace('fer', 'FER').replace('mediapipe', 'MediaPipe').replace('opencv', 'OpenCV')] = weight

        return weights

    def shutdown(self) -> None:
        """Clean up all models."""
        for model in self.models:
            try:
                model.shutdown()
            except:
                pass

        if self.facs_analyzer:
            try:
                self.facs_analyzer.shutdown()
            except:
                pass
