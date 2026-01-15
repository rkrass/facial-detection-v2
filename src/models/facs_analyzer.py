"""FACS (Facial Action Coding System) analyzer using py-feat."""

from typing import List, Optional
import numpy as np
import cv2

from ..data.models import ActionUnit, FaceRegion


class FACSAnalyzer:
    """Analyzes facial Action Units using py-feat library."""

    def __init__(self):
        """Initialize FACS analyzer."""
        self.detector = None
        self.is_initialized = False

    def initialize(self) -> bool:
        """Initialize py-feat detector."""
        try:
            from feat import Detector
            # Initialize with all detection models
            self.detector = Detector(
                face_model="retinaface",
                landmark_model="mobilenet",
                au_model="xgb",  # Action Unit detection
                emotion_model="resmasknet",
            )
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize py-feat: {e}")
            print("FACS analysis will be disabled. Install with: pip install py-feat")
            self.is_initialized = False
            return False

    def detect_action_units(
        self,
        frame: np.ndarray,
        face_region: FaceRegion
    ) -> List[ActionUnit]:
        """
        Detect facial Action Units.

        Args:
            frame: Full frame image
            face_region: Region containing the face

        Returns:
            List of detected Action Units
        """
        if not self.is_initialized:
            return []

        try:
            # Extract face region
            x, y, w, h = face_region.to_tuple()
            face_img = frame[y:y+h, x:x+w]

            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

            # Detect AUs
            results = self.detector.detect_image(face_rgb)

            if results is None or len(results) == 0:
                return []

            # Extract AU columns (they start with "AU")
            au_columns = [col for col in results.columns if col.startswith("AU") and col[2:].isdigit()]

            action_units = []
            for au_col in au_columns:
                au_number = int(au_col[2:])  # Extract AU number (e.g., "AU01" -> 1)
                intensity = float(results[au_col].iloc[0])

                # Threshold for AU presence (typically > 0.5)
                present = intensity > 0.5

                action_units.append(ActionUnit(
                    au_number=au_number,
                    intensity=intensity,
                    present=present
                ))

            return action_units

        except Exception as e:
            print(f"FACS detection error: {e}")
            return []

    def get_deception_aus(self) -> List[int]:
        """
        Get Action Units commonly associated with deception.

        Returns:
            List of AU numbers
        """
        return [
            4,   # Brow Lowerer (inner brow down)
            15,  # Lip Corner Depressor
            23,  # Lip Tightener
            24,  # Lip Pressor
            9,   # Nose Wrinkler
            10,  # Upper Lip Raiser
        ]

    def shutdown(self) -> None:
        """Clean up resources."""
        self.detector = None
        self.is_initialized = False
