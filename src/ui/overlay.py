"""Transparent overlay for displaying face detection results."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath
from typing import Optional, List
import numpy as np

from ..data.models import FrameAnalysis


# MediaPipe face mesh connection indices for drawing
FACE_MESH_CONNECTIONS = [
    # Face oval
    (10, 338), (338, 297), (297, 332), (332, 284), (284, 251), (251, 389),
    (389, 356), (356, 454), (454, 323), (323, 361), (361, 288), (288, 397),
    (397, 365), (365, 379), (379, 378), (378, 400), (400, 377), (377, 152),
    (152, 148), (148, 176), (176, 149), (149, 150), (150, 136), (136, 172),
    (172, 58), (58, 132), (132, 93), (93, 234), (234, 127), (127, 162),
    (162, 21), (21, 54), (54, 103), (103, 67), (67, 109), (109, 10),
    # Lips outer
    (61, 146), (146, 91), (91, 181), (181, 84), (84, 17), (17, 314),
    (314, 405), (405, 321), (321, 375), (375, 291), (291, 61),
    # Lips inner
    (78, 95), (95, 88), (88, 178), (178, 87), (87, 14), (14, 317),
    (317, 402), (402, 318), (318, 324), (324, 308), (308, 78),
    # Left eye
    (33, 246), (246, 161), (161, 160), (160, 159), (159, 158), (158, 157),
    (157, 173), (173, 133), (133, 155), (155, 154), (154, 153), (153, 145),
    (145, 144), (144, 163), (163, 7), (7, 33),
    # Right eye
    (263, 466), (466, 388), (388, 387), (387, 386), (386, 385), (385, 384),
    (384, 398), (398, 362), (362, 382), (382, 381), (381, 380), (380, 374),
    (374, 373), (373, 390), (390, 249), (249, 263),
    # Left eyebrow
    (46, 53), (53, 52), (52, 65), (65, 55), (55, 70), (70, 63), (63, 105),
    (105, 66), (66, 107),
    # Right eyebrow
    (276, 283), (283, 282), (282, 295), (295, 285), (285, 300), (300, 293),
    (293, 334), (334, 296), (296, 336),
    # Nose
    (168, 6), (6, 197), (197, 195), (195, 5), (5, 4), (4, 1), (1, 19),
    (19, 94), (94, 2),
]


class TransparentOverlay(QWidget):
    """Transparent overlay window that displays face detection results."""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.frame_analysis: Optional[FrameAnalysis] = None
        self.show_mesh = True  # Toggle for facial mesh display (enabled by default)

        # Face tracking - use spatial tracking instead of index-based
        self.tracked_faces = {}  # track_id -> {x, y, w, h, emotion, history, age}
        self.next_track_id = 0
        self.smoothing_alpha = 0.15  # Exponential smoothing factor (lower = smoother)
        self.max_track_distance = 100  # Max pixels to match same face
        self.track_timeout = 30  # Frames before removing unmatched track

        # Get overlay configuration
        overlay_config = config.get('ui', {}).get('overlay', {})
        self.bbox_config = overlay_config.get('bbox', {})
        self.label_config = overlay_config.get('label', {})

        self.init_ui()

    def init_ui(self):
        """Initialize the overlay window."""
        # Set window flags for transparent overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )

        # Make window transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Set to fullscreen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def update_analysis(self, frame_analysis: FrameAnalysis):
        """
        Update overlay with new frame analysis using spatial tracking.

        Args:
            frame_analysis: Latest frame analysis
        """
        from collections import Counter
        import math

        # Mark all tracks as unmatched
        for track_id in self.tracked_faces:
            self.tracked_faces[track_id]['matched'] = False

        # Match detected faces to existing tracks based on position
        for face in frame_analysis.faces:
            face_cx = face.region.x + face.region.width / 2
            face_cy = face.region.y + face.region.height / 2

            # Find closest existing track
            best_track_id = None
            best_distance = self.max_track_distance

            for track_id, track in self.tracked_faces.items():
                if track['matched']:
                    continue
                track_cx = track['x'] + track['w'] / 2
                track_cy = track['y'] + track['h'] / 2
                distance = math.sqrt((face_cx - track_cx)**2 + (face_cy - track_cy)**2)
                if distance < best_distance:
                    best_distance = distance
                    best_track_id = track_id

            if best_track_id is not None:
                # Update existing track with exponential smoothing
                track = self.tracked_faces[best_track_id]
                alpha = self.smoothing_alpha
                track['x'] = track['x'] * (1 - alpha) + face.region.x * alpha
                track['y'] = track['y'] * (1 - alpha) + face.region.y * alpha
                track['w'] = track['w'] * (1 - alpha) + face.region.width * alpha
                track['h'] = track['h'] * (1 - alpha) + face.region.height * alpha
                track['emotion_history'].append(face.emotion)
                if len(track['emotion_history']) > 15:
                    track['emotion_history'] = track['emotion_history'][-15:]
                track['matched'] = True
                track['age'] = 0
                track['face_data'] = face  # Store current face data
            else:
                # Create new track
                self.tracked_faces[self.next_track_id] = {
                    'x': float(face.region.x),
                    'y': float(face.region.y),
                    'w': float(face.region.width),
                    'h': float(face.region.height),
                    'emotion_history': [face.emotion],
                    'matched': True,
                    'age': 0,
                    'face_data': face
                }
                self.next_track_id += 1

        # Age unmatched tracks and remove old ones
        tracks_to_remove = []
        for track_id, track in self.tracked_faces.items():
            if not track['matched']:
                track['age'] += 1
                if track['age'] > self.track_timeout:
                    tracks_to_remove.append(track_id)

        for track_id in tracks_to_remove:
            del self.tracked_faces[track_id]

        # Apply smoothed positions back to faces for rendering
        for face in frame_analysis.faces:
            face_cx = face.region.x + face.region.width / 2
            face_cy = face.region.y + face.region.height / 2

            # Find the track for this face
            for track_id, track in self.tracked_faces.items():
                if track.get('face_data') == face:
                    # Apply smoothed position
                    face.region.x = int(track['x'])
                    face.region.y = int(track['y'])
                    face.region.width = int(track['w'])
                    face.region.height = int(track['h'])

                    # Apply smoothed emotion (most common in history)
                    if track['emotion_history']:
                        emotion_counts = Counter(track['emotion_history'])
                        face.emotion = emotion_counts.most_common(1)[0][0]
                    break

        self.frame_analysis = frame_analysis
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Paint the overlay."""
        if not self.frame_analysis or not self.frame_analysis.faces:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw each detected face
        for face in self.frame_analysis.faces:
            self._draw_face(painter, face)

        painter.end()

    def _draw_face(self, painter: QPainter, face):
        """Draw bounding box, label, and optional mesh for a face."""
        # Determine color based on deception
        if face.is_deceptive:
            color = self.bbox_config.get('deception_color', [255, 0, 0])
        else:
            color = self.bbox_config.get('color', [0, 255, 0])

        # Create pen for bounding box
        pen = QPen(QColor(*color))
        pen.setWidth(self.bbox_config.get('thickness', 2))
        painter.setPen(pen)

        # Draw bounding box
        rect = QRect(
            face.region.x,
            face.region.y,
            face.region.width,
            face.region.height
        )
        painter.drawRect(rect)

        # Draw facial mesh if enabled
        self._draw_mesh(painter, face)

        # Draw label
        self._draw_label(painter, face, color)

    def _draw_label(self, painter: QPainter, face, color):
        """Draw emotion label with multi-model predictions above face."""
        font_size = self.label_config.get('font_size', 12)
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_height = metrics.height()
        padding = 5
        bg_opacity = int(self.label_config.get('background_opacity', 0.7) * 255)

        # Build multi-model display
        model_colors = {
            'DeepFace': [0, 200, 255],   # Cyan
            'OpenCV': [255, 200, 0],      # Orange
            'MediaPipe': [200, 100, 255], # Purple
            'FER': [100, 255, 100]        # Green
        }

        # Get model predictions
        predictions = face.model_predictions if hasattr(face, 'model_predictions') else []

        if predictions and len(predictions) > 0:
            # Draw individual model predictions
            label_y = face.region.y - (text_height + padding * 2) * len(predictions) - padding
            if label_y < 0:
                label_y = face.region.y + face.region.height + padding

            for pred in predictions:
                model_name = pred.model_name
                emotion = pred.emotion.upper()
                conf = pred.confidence

                label_text = f"{model_name}: {emotion} ({conf:.0%})"
                text_width = metrics.horizontalAdvance(label_text)

                # Draw background
                bg_color = QColor(0, 0, 0, bg_opacity)
                painter.fillRect(
                    face.region.x,
                    label_y,
                    text_width + 2 * padding,
                    text_height + 2 * padding,
                    bg_color
                )

                # Draw text with model-specific color
                model_color = model_colors.get(model_name, color)
                painter.setPen(QColor(*model_color))
                painter.drawText(
                    face.region.x + padding,
                    label_y + text_height,
                    label_text
                )

                label_y += text_height + padding * 2

            # Draw ensemble result if deceptive
            if face.is_deceptive:
                deception_text = "⚠ DECEPTION"
                text_width = metrics.horizontalAdvance(deception_text)
                painter.fillRect(
                    face.region.x,
                    label_y,
                    text_width + 2 * padding,
                    text_height + 2 * padding,
                    QColor(255, 0, 0, bg_opacity)
                )
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(
                    face.region.x + padding,
                    label_y + text_height,
                    deception_text
                )
        else:
            # Fallback to single label
            label_parts = []
            if self.label_config.get('show_emotion', True):
                label_parts.append(face.emotion.upper())
            if self.label_config.get('show_confidence', True):
                label_parts.append(f"{face.confidence:.0%}")
            if face.is_deceptive:
                label_parts.append("DECEPTION")

            label_text = " | ".join(label_parts)
            text_width = metrics.horizontalAdvance(label_text)

            label_x = face.region.x
            label_y = face.region.y - text_height - padding
            if label_y < 0:
                label_y = face.region.y + face.region.height + padding

            bg_color = QColor(0, 0, 0, bg_opacity)
            painter.fillRect(
                label_x,
                label_y,
                text_width + 2 * padding,
                text_height + 2 * padding,
                bg_color
            )

            painter.setPen(QColor(*color))
            painter.drawText(
                label_x + padding,
                label_y + text_height,
                label_text
            )

    def _draw_mesh(self, painter: QPainter, face):
        """Draw facial mesh landmarks if available."""
        if not self.show_mesh:
            return

        if face.landmarks is None:
            # Debug: landmarks not available
            return

        if len(face.landmarks) < 468:
            # Not enough landmarks
            return

        # Get face region and expand it to match MediaPipe's extraction area
        region = face.region
        landmarks = face.landmarks

        # MediaPipe uses 50% expansion, so we need to draw in expanded coordinates
        expand = 0.5
        expanded_x = int(region.x - region.width * expand)
        expanded_y = int(region.y - region.height * expand)
        expanded_w = int(region.width * (1 + 2 * expand))
        expanded_h = int(region.height * (1 + 2 * expand))

        # Set pen for mesh lines - thicker and more visible
        mesh_pen = QPen(QColor(0, 255, 255, 220))  # Cyan
        mesh_pen.setWidth(2)
        painter.setPen(mesh_pen)

        # Draw mesh connections
        for start_idx, end_idx in FACE_MESH_CONNECTIONS:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                # Scale landmarks to expanded region
                x1 = int(expanded_x + landmarks[start_idx][0] * expanded_w)
                y1 = int(expanded_y + landmarks[start_idx][1] * expanded_h)
                x2 = int(expanded_x + landmarks[end_idx][0] * expanded_w)
                y2 = int(expanded_y + landmarks[end_idx][1] * expanded_h)

                painter.drawLine(x1, y1, x2, y2)

        # Draw landmark points - larger and more visible
        point_pen = QPen(QColor(0, 255, 128, 255))  # Bright green
        point_pen.setWidth(4)
        painter.setPen(point_pen)

        # Draw fewer points for clarity (key facial landmarks)
        key_landmarks = [33, 133, 362, 263, 1, 61, 291, 199]  # Eyes, nose, mouth corners
        for idx in key_landmarks:
            if idx < len(landmarks):
                x = int(expanded_x + landmarks[idx][0] * expanded_w)
                y = int(expanded_y + landmarks[idx][1] * expanded_h)
                painter.drawEllipse(x-3, y-3, 6, 6)

    def toggle_mesh(self):
        """Toggle facial mesh display on/off."""
        self.show_mesh = not self.show_mesh
        self.update()
        return self.show_mesh

    def set_mesh_visible(self, visible: bool):
        """Set facial mesh visibility."""
        self.show_mesh = visible
        self.update()
