"""Face detection coordination using OpenCV and MediaPipe."""

import cv2
import numpy as np
from typing import List, Optional
import os

from ..data.models import FaceRegion


class FaceDetector:
    """Detects faces in frames using multiple detection methods."""

    def __init__(self, method: str = "opencv"):
        """
        Initialize face detector.

        Args:
            method: Detection method ('opencv', 'mediapipe', 'both')
        """
        self.method = method

        # OpenCV face detection
        self.opencv_cascade = None

        # MediaPipe face detection (new tasks API)
        self.mp_face_detector = None

        self.is_initialized = False

        # Frame caching for consistent results on static images
        self._prev_frame_small = None
        self._prev_faces = []

    def initialize(self) -> bool:
        """Initialize face detection models."""
        try:
            if self.method in ["opencv", "both"]:
                # Load OpenCV Haar Cascade
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.opencv_cascade = cv2.CascadeClassifier(cascade_path)

                if self.opencv_cascade.empty():
                    print("Failed to load OpenCV Haar Cascade")
                    return False

            if self.method in ["mediapipe", "both"]:
                try:
                    import mediapipe as mp

                    # Find face detector model (blaze_face_short_range.tflite)
                    model_paths = [
                        os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'blaze_face_short_range.tflite'),
                        os.path.join(os.getcwd(), 'models', 'blaze_face_short_range.tflite'),
                    ]

                    model_path = None
                    for path in model_paths:
                        if os.path.exists(path):
                            model_path = path
                            break

                    if model_path:
                        base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
                        options = mp.tasks.vision.FaceDetectorOptions(
                            base_options=base_options,
                            running_mode=mp.tasks.vision.RunningMode.IMAGE,
                            min_detection_confidence=0.5
                        )
                        self.mp_face_detector = mp.tasks.vision.FaceDetector.create_from_options(options)
                    else:
                        print("MediaPipe face detector model not found, skipping MediaPipe")
                        if self.method == "mediapipe":
                            return False
                except Exception as e:
                    print(f"MediaPipe face detection init error: {e}")
                    if self.method == "mediapipe":
                        return False

            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Failed to initialize face detector: {e}")
            self.is_initialized = False
            return False

    def detect_faces(self, frame: np.ndarray) -> List[FaceRegion]:
        """
        Detect faces in frame.

        Args:
            frame: Image frame to process

        Returns:
            List of detected face regions
        """
        if not self.is_initialized:
            return []

        if self.method == "opencv":
            return self._detect_opencv(frame)
        elif self.method == "mediapipe":
            return self._detect_mediapipe(frame)
        elif self.method == "both":
            # Combine results from both methods
            opencv_faces = self._detect_opencv(frame)
            mp_faces = self._detect_mediapipe(frame)
            return self._merge_detections(opencv_faces, mp_faces)
        else:
            return []

    def _detect_opencv(self, frame: np.ndarray) -> List[FaceRegion]:
        """Detect faces using OpenCV."""
        if self.opencv_cascade is None:
            return []

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply histogram equalization for better detection consistency
            gray = cv2.equalizeHist(gray)

            # Check if frame is similar to previous (for static image stability)
            # Use downsampled comparison to tolerate minor screen capture variations
            small = cv2.resize(gray, (32, 32))
            if self._prev_frame_small is not None and self._prev_faces:
                diff = cv2.absdiff(small, self._prev_frame_small)
                if np.mean(diff) < 10:  # Similar frame (tolerate minor variations)
                    return self._prev_faces

            # Single-pass detection for consistent results
            faces = self.opencv_cascade.detectMultiScale(
                gray,
                scaleFactor=1.02,
                minNeighbors=15,
                minSize=(35, 35),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            # Convert to FaceRegion objects with aspect ratio filtering
            face_regions = []
            for (x, y, w, h) in faces:
                # Filter by aspect ratio - faces are roughly square (0.8 to 1.25)
                aspect_ratio = w / h if h > 0 else 0
                if 0.85 <= aspect_ratio <= 1.2:
                    face_regions.append(FaceRegion(
                        x=int(x),
                        y=int(y),
                        width=int(w),
                        height=int(h),
                        confidence=0.9  # OpenCV doesn't provide confidence
                    ))

            # Cache results for static image stability
            self._prev_frame_small = small
            self._prev_faces = face_regions

            return face_regions

        except Exception as e:
            print(f"OpenCV face detection error: {e}")
            return []

    def _nms_faces(self, faces, overlap_threshold=0.3):
        """Apply non-maximum suppression to raw face detections."""
        if len(faces) == 0:
            return []

        # Convert to list of tuples if numpy array
        faces = [tuple(f) for f in faces]

        # Sort by area (larger faces first)
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)

        kept = []
        for face in faces:
            x1, y1, w1, h1 = face
            is_duplicate = False

            for kept_face in kept:
                x2, y2, w2, h2 = kept_face

                # Calculate IoU
                xi1 = max(x1, x2)
                yi1 = max(y1, y2)
                xi2 = min(x1 + w1, x2 + w2)
                yi2 = min(y1 + h1, y2 + h2)

                inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
                union_area = w1 * h1 + w2 * h2 - inter_area

                if union_area > 0 and inter_area / union_area > overlap_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                kept.append(face)

        return kept

    def _detect_mediapipe(self, frame: np.ndarray) -> List[FaceRegion]:
        """Detect faces using MediaPipe tasks API."""
        if self.mp_face_detector is None:
            return []

        try:
            import mediapipe as mp

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            # Detect faces
            results = self.mp_face_detector.detect(mp_image)

            if not results.detections:
                return []

            # Convert to FaceRegion objects
            h, w, _ = frame.shape
            face_regions = []

            for detection in results.detections:
                bbox = detection.bounding_box

                # Get absolute coordinates
                x = bbox.origin_x
                y = bbox.origin_y
                width = bbox.width
                height = bbox.height

                # Ensure coordinates are within frame bounds
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)

                face_regions.append(FaceRegion(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    confidence=detection.categories[0].score if detection.categories else 0.9
                ))

            return face_regions

        except Exception as e:
            print(f"MediaPipe face detection error: {e}")
            return []

    def _merge_detections(
        self,
        faces1: List[FaceRegion],
        faces2: List[FaceRegion],
        iou_threshold: float = 0.5
    ) -> List[FaceRegion]:
        """
        Merge face detections from two methods using NMS.

        Args:
            faces1: Face regions from first detector
            faces2: Face regions from second detector
            iou_threshold: IoU threshold for considering faces as duplicates

        Returns:
            Merged list of face regions
        """
        all_faces = faces1 + faces2

        if len(all_faces) == 0:
            return []

        # Sort by confidence
        all_faces.sort(key=lambda f: f.confidence, reverse=True)

        # Non-maximum suppression
        kept_faces = []

        for face in all_faces:
            # Check if this face overlaps significantly with any kept face
            is_duplicate = False
            for kept_face in kept_faces:
                iou = self._calculate_iou(face, kept_face)
                if iou > iou_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                kept_faces.append(face)

        return kept_faces

    def _calculate_iou(self, face1: FaceRegion, face2: FaceRegion) -> float:
        """Calculate Intersection over Union between two face regions."""
        # Calculate intersection
        x1 = max(face1.x, face2.x)
        y1 = max(face1.y, face2.y)
        x2 = min(face1.x + face1.width, face2.x + face2.width)
        y2 = min(face1.y + face1.height, face2.y + face2.height)

        intersection = max(0, x2 - x1) * max(0, y2 - y1)

        # Calculate union
        area1 = face1.width * face1.height
        area2 = face2.width * face2.height
        union = area1 + area2 - intersection

        if union == 0:
            return 0.0

        return intersection / union

    def shutdown(self) -> None:
        """Clean up resources."""
        if self.mp_face_detector:
            self.mp_face_detector.close()
