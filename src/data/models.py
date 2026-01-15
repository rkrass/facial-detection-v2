"""Data models and structures for the facial detection application."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np


@dataclass
class FaceRegion:
    """Represents a detected face region in a frame."""
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0

    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to (x, y, w, h) tuple."""
        return (self.x, self.y, self.width, self.height)

    def center(self) -> Tuple[int, int]:
        """Get center point of face region."""
        return (self.x + self.width // 2, self.y + self.height // 2)


@dataclass
class EmotionPrediction:
    """Emotion prediction from a single model."""
    model_name: str
    emotion: str
    confidence: float
    all_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ActionUnit:
    """FACS Action Unit detection."""
    au_number: int
    intensity: float  # 0-1 scale
    present: bool  # Whether AU is active


@dataclass
class FaceAnalysis:
    """Complete analysis of a single face."""
    face_id: int
    region: FaceRegion
    emotion: str
    confidence: float
    model_predictions: List[EmotionPrediction] = field(default_factory=list)
    action_units: List[ActionUnit] = field(default_factory=list)
    is_deceptive: bool = False
    deception_confidence: float = 0.0
    deception_reason: Optional[str] = None
    landmarks: Optional[np.ndarray] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "face_id": self.face_id,
            "region": {
                "x": self.region.x,
                "y": self.region.y,
                "width": self.region.width,
                "height": self.region.height,
                "confidence": self.region.confidence
            },
            "emotion": self.emotion,
            "confidence": self.confidence,
            "model_predictions": [
                {
                    "model": p.model_name,
                    "emotion": p.emotion,
                    "confidence": p.confidence,
                    "scores": p.all_scores
                }
                for p in self.model_predictions
            ],
            "action_units": [
                {
                    "au": au.au_number,
                    "intensity": au.intensity,
                    "present": au.present
                }
                for au in self.action_units
            ],
            "deception": {
                "is_deceptive": self.is_deceptive,
                "confidence": self.deception_confidence,
                "reason": self.deception_reason
            },
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class FrameAnalysis:
    """Analysis of all faces in a single frame."""
    frame_number: int
    timestamp: datetime
    faces: List[FaceAnalysis] = field(default_factory=list)
    fps: float = 0.0
    processing_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "frame_number": self.frame_number,
            "timestamp": self.timestamp.isoformat(),
            "fps": self.fps,
            "processing_time_ms": self.processing_time_ms,
            "face_count": len(self.faces),
            "faces": [face.to_dict() for face in self.faces]
        }


@dataclass
class SessionMetadata:
    """Metadata for a monitoring session."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_frames: int = 0
    total_faces_detected: int = 0
    deception_events: int = 0
    average_fps: float = 0.0
    config_snapshot: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_frames": self.total_frames,
            "total_faces_detected": self.total_faces_detected,
            "deception_events": self.deception_events,
            "average_fps": self.average_fps,
            "config": self.config_snapshot
        }


@dataclass
class PerformanceMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_mb: float
    current_fps: float
    target_fps: float
    dropped_frames: int = 0
