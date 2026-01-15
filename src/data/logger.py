"""Session logging with optional encryption."""

import json
import os
from datetime import datetime
from typing import Optional
from pathlib import Path
import numpy as np

from .models import FrameAnalysis, SessionMetadata
from .encryption import DataEncryption


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types."""
    def default(self, obj):
        # Handle numpy boolean first (must be before generic bool check)
        if isinstance(obj, (np.bool_, np.bool8)) if hasattr(np, 'bool8') else isinstance(obj, np.bool_):
            return bool(obj)
        # Handle numpy integers
        if isinstance(obj, np.integer):
            return int(obj)
        # Handle numpy floats
        if isinstance(obj, np.floating):
            return float(obj)
        # Handle numpy arrays
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # Handle any numpy generic type (catch-all for numpy scalars)
        if isinstance(obj, np.generic):
            return obj.item()
        # Handle datetime objects
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super(NumpyEncoder, self).default(obj)


class SessionLogger:
    """Logs session data to files with optional encryption."""

    def __init__(self, config: dict):
        """
        Initialize session logger.

        Args:
            config: Logging configuration
        """
        self.config = config
        logging_config = config.get('logging', {})

        self.enabled = logging_config.get('enabled', True)
        self.directory = logging_config.get('directory', 'sessions')
        self.format = logging_config.get('format', 'json')
        self.encrypt = logging_config.get('encrypt', True)
        self.autosave_interval = logging_config.get('autosave_interval', 60)

        # What to log
        self.log_emotions = logging_config.get('log_emotions', True)
        self.log_confidence = logging_config.get('log_confidence', True)
        self.log_aus = logging_config.get('log_aus', True)
        self.log_deception_events = logging_config.get('log_deception_events', True)
        self.log_fps = logging_config.get('log_fps', True)

        # Session data
        self.session_metadata: Optional[SessionMetadata] = None
        self.frame_logs = []
        self.current_file_path = None

        # Encryption
        self.encryption = None
        if self.encrypt:
            # Default password - in production, this should be user-provided
            default_password = "facial-detection-session-2024"
            self.encryption = DataEncryption(default_password)

        # Create session directory
        if self.enabled:
            Path(self.directory).mkdir(parents=True, exist_ok=True)

    def start_session(self, session_id: str, config_snapshot: dict) -> None:
        """
        Start a new logging session.

        Args:
            session_id: Unique session identifier
            config_snapshot: Snapshot of current configuration
        """
        if not self.enabled:
            return

        self.session_metadata = SessionMetadata(
            session_id=session_id,
            start_time=datetime.now(),
            config_snapshot=config_snapshot
        )

        self.frame_logs = []

        # Create log file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{session_id}_{timestamp}.json"

        if self.encrypt:
            filename += ".enc"

        self.current_file_path = os.path.join(self.directory, filename)

    def log_frame(self, frame_analysis: FrameAnalysis) -> None:
        """
        Log analysis of a single frame.

        Args:
            frame_analysis: Frame analysis to log
        """
        if not self.enabled or self.session_metadata is None:
            return

        # Filter what to log based on configuration
        log_entry = self._filter_frame_data(frame_analysis)

        self.frame_logs.append(log_entry)

        # Update session metadata
        self.session_metadata.total_frames += 1
        self.session_metadata.total_faces_detected += len(frame_analysis.faces)

        # Count deception events
        for face in frame_analysis.faces:
            if face.is_deceptive:
                self.session_metadata.deception_events += 1

    def _filter_frame_data(self, frame_analysis: FrameAnalysis) -> dict:
        """Filter frame data based on logging configuration."""
        data = {
            "frame_number": frame_analysis.frame_number,
            "timestamp": frame_analysis.timestamp.isoformat(),
        }

        if self.log_fps:
            data["fps"] = frame_analysis.fps
            data["processing_time_ms"] = frame_analysis.processing_time_ms

        data["faces"] = []

        for face in frame_analysis.faces:
            face_data = {
                "face_id": face.face_id,
                "region": {
                    "x": face.region.x,
                    "y": face.region.y,
                    "width": face.region.width,
                    "height": face.region.height
                }
            }

            if self.log_emotions:
                face_data["emotion"] = face.emotion

            if self.log_confidence:
                face_data["confidence"] = face.confidence

            if self.log_aus and face.action_units:
                face_data["action_units"] = [
                    {
                        "au": au.au_number,
                        "intensity": au.intensity,
                        "present": au.present
                    }
                    for au in face.action_units
                ]

            if self.log_deception_events:
                face_data["deception"] = {
                    "is_deceptive": face.is_deceptive,
                    "confidence": face.deception_confidence,
                    "reason": face.deception_reason
                }

            data["faces"].append(face_data)

        return data

    def save_session(self) -> None:
        """Save current session to file."""
        if not self.enabled or self.session_metadata is None:
            return

        # Calculate average FPS
        if self.frame_logs:
            total_fps = sum(frame.get("fps", 0) for frame in self.frame_logs)
            self.session_metadata.average_fps = total_fps / len(self.frame_logs)

        # End session
        self.session_metadata.end_time = datetime.now()

        # Create complete log
        complete_log = {
            "metadata": self.session_metadata.to_dict(),
            "frames": self.frame_logs
        }

        # Convert to JSON (use NumpyEncoder to handle numpy types)
        json_data = json.dumps(complete_log, indent=2, cls=NumpyEncoder)

        # Save to file
        if self.encrypt and self.encryption:
            # Encrypt and save
            encrypted = self.encryption.encrypt(json_data.encode('utf-8'))
            with open(self.current_file_path, 'wb') as f:
                f.write(encrypted)
        else:
            # Save plain text
            with open(self.current_file_path, 'w') as f:
                f.write(json_data)

        print(f"Session saved to: {self.current_file_path}")

    def load_session(self, file_path: str) -> dict:
        """
        Load a session from file.

        Args:
            file_path: Path to session file

        Returns:
            Session data dictionary
        """
        if file_path.endswith('.enc'):
            # Decrypt and load
            if not self.encryption:
                raise ValueError("Encryption not initialized")

            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted = self.encryption.decrypt(encrypted_data)
            return json.loads(decrypted.decode('utf-8'))
        else:
            # Load plain text
            with open(file_path, 'r') as f:
                return json.load(f)
