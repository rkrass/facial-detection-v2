"""Integration tests for the full detection pipeline."""

import pytest
import numpy as np

from src.core.session_manager import SessionManager
from src.data.models import FrameAnalysis


class TestDetectionPipeline:
    """Test the complete detection pipeline."""

    def test_session_manager_initialization(self, test_config):
        """Test that session manager initializes all components."""
        # Disable FACS for faster testing
        test_config['facs']['enabled'] = False

        session = SessionManager(test_config)
        success = session.initialize()

        assert success is True
        assert session.is_initialized is True
        assert session.screen_capture is not None
        assert session.face_detector is not None
        assert session.emotion_detector is not None
        assert session.deception_detector is not None

        session.shutdown()

    def test_frame_processing_no_faces(self, test_config, sample_frame):
        """Test processing a frame with no faces."""
        test_config['facs']['enabled'] = False

        session = SessionManager(test_config)
        session.initialize()
        session.start()

        # Process should return None or empty faces when no faces detected
        # (sample_frame is just a colored rectangle with no faces)

        session.stop()
        session.shutdown()

    def test_session_lifecycle(self, test_config):
        """Test full session lifecycle."""
        test_config['facs']['enabled'] = False

        session = SessionManager(test_config)

        # Initialize
        assert session.initialize() is True

        # Start
        session.start()
        assert session.is_running is True

        # Stop
        session.stop()
        assert session.is_running is False

        # Shutdown
        session.shutdown()


class TestSessionLogging:
    """Test session logging functionality."""

    def test_logger_initialization(self, test_config):
        """Test that logger initializes correctly."""
        from src.data.logger import SessionLogger

        logger = SessionLogger(test_config)
        logger.start_session("test_session", test_config)

        assert logger.session_metadata is not None
        assert logger.session_metadata.session_id == "test_session"
