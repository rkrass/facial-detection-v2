"""Session management coordinating all detection components."""

import time
import uuid
from datetime import datetime
from typing import Optional
import numpy as np

from ..data.models import FrameAnalysis, FaceAnalysis
from ..core.screen_capture import ScreenCapture
from ..core.face_detector import FaceDetector
from ..detection.emotion_detector import EmotionDetector
from ..detection.deception import DeceptionDetector
from ..data.logger import SessionLogger
from ..utils.performance import PerformanceMonitor


class SessionManager:
    """Manages a detection session from start to finish."""

    def __init__(self, config: dict):
        """
        Initialize session manager.

        Args:
            config: Application configuration
        """
        self.config = config
        self.session_id = str(uuid.uuid4())[:8]

        # Components
        self.screen_capture: Optional[ScreenCapture] = None
        self.face_detector: Optional[FaceDetector] = None
        self.emotion_detector: Optional[EmotionDetector] = None
        self.deception_detector: Optional[DeceptionDetector] = None
        self.logger: Optional[SessionLogger] = None
        self.performance: Optional[PerformanceMonitor] = None

        # Session state
        self.is_running = False
        self.is_initialized = False
        self.frame_count = 0
        self.last_process_time = 0

        # Frame callback for UI updates
        self.frame_callback = None

    def initialize(self) -> bool:
        """Initialize all components."""
        try:
            print(f"\n{'='*60}")
            print(f"Initializing Session: {self.session_id}")
            print(f"{'='*60}\n")

            # Initialize screen capture
            screen_config = self.config.get('screen_capture', {})
            self.screen_capture = ScreenCapture(
                monitor_index=screen_config.get('monitor', 0),
                region=screen_config.get('region')
            )
            print("✓ Screen capture initialized")

            # Initialize face detector (use OpenCV for small images)
            self.face_detector = FaceDetector(method="opencv")
            if not self.face_detector.initialize():
                print("ERROR: Failed to initialize face detector")
                return False
            print("✓ Face detector initialized")

            # Initialize emotion detector
            self.emotion_detector = EmotionDetector(self.config)
            if not self.emotion_detector.initialize():
                print("ERROR: Failed to initialize emotion detector")
                return False

            # Initialize deception detector
            self.deception_detector = DeceptionDetector(self.config)
            print("✓ Deception detector initialized")

            # Initialize performance monitor
            perf_config = self.config.get('performance', {})
            self.performance = PerformanceMonitor(
                initial_fps=perf_config.get('initial_fps', 10),
                min_fps=perf_config.get('min_fps', 5),
                max_fps=perf_config.get('max_fps', 30),
                target_cpu_percent=perf_config.get('target_cpu_percent', 70)
            )
            print("✓ Performance monitor initialized")

            # Initialize logger
            self.logger = SessionLogger(self.config)
            self.logger.start_session(self.session_id, self.config)
            print("✓ Session logger initialized")

            self.is_initialized = True
            print(f"\n{'='*60}")
            print("All components initialized successfully!")
            print(f"{'='*60}\n")
            return True

        except Exception as e:
            print(f"Failed to initialize session: {e}")
            import traceback
            traceback.print_exc()
            self.is_initialized = False
            return False

    def start(self, frame_callback=None) -> None:
        """
        Start the detection session.

        Args:
            frame_callback: Optional callback function(frame_analysis) for UI updates
        """
        if not self.is_initialized:
            print("ERROR: Session not initialized")
            return

        self.is_running = True
        self.frame_callback = frame_callback
        self.last_process_time = time.time()

        print(f"Session {self.session_id} started")

    def process_frame(self) -> Optional[FrameAnalysis]:
        """
        Process a single frame.

        Returns:
            FrameAnalysis or None if frame should be skipped
        """
        if not self.is_running or not self.is_initialized:
            return None

        # Check if we should process this frame (adaptive frame rate)
        current_time = time.time()
        if not self.performance.should_process_frame(self.last_process_time):
            return None

        process_start = time.time()

        try:
            # Capture screen
            frame = self.screen_capture.capture_frame()
            if frame is None:
                return None

            # Detect faces
            face_regions = self.face_detector.detect_faces(frame)

            # Analyze each face
            face_analyses = []
            for i, face_region in enumerate(face_regions):
                # Analyze emotion
                face_analysis = self.emotion_detector.analyze_face(
                    frame,
                    face_region,
                    face_id=i
                )

                if face_analysis:
                    # Analyze for deception
                    is_deceptive, deception_conf, reason = self.deception_detector.analyze_for_deception(
                        i,
                        face_analysis
                    )

                    face_analysis.is_deceptive = is_deceptive
                    face_analysis.deception_confidence = deception_conf
                    face_analysis.deception_reason = reason

                    face_analyses.append(face_analysis)

            # Calculate processing time
            process_end = time.time()
            processing_time_ms = (process_end - process_start) * 1000

            # Record frame time for adaptive FPS
            self.performance.record_frame_time(process_end - process_start)

            # Create frame analysis
            frame_analysis = FrameAnalysis(
                frame_number=self.frame_count,
                timestamp=datetime.now(),
                faces=face_analyses,
                fps=self.performance.current_fps,
                processing_time_ms=processing_time_ms
            )

            # Log frame
            self.logger.log_frame(frame_analysis)

            # Update state
            self.frame_count += 1
            self.last_process_time = current_time

            # Adapt frame rate
            if self.config.get('performance', {}).get('adaptive', True):
                self.performance.adapt_frame_rate()

            # Call frame callback if provided
            if self.frame_callback:
                self.frame_callback(frame_analysis, frame)

            return frame_analysis

        except Exception as e:
            print(f"Error processing frame: {e}")
            import traceback
            traceback.print_exc()
            return None

    def stop(self) -> None:
        """Stop the detection session."""
        self.is_running = False
        print(f"\nSession {self.session_id} stopped")
        print(f"Total frames processed: {self.frame_count}")

        # Save session logs
        if self.logger:
            self.logger.save_session()

    def shutdown(self) -> None:
        """Clean up all resources."""
        self.stop()

        if self.screen_capture:
            self.screen_capture.close()

        if self.face_detector:
            self.face_detector.shutdown()

        if self.emotion_detector:
            self.emotion_detector.shutdown()

        if self.deception_detector:
            self.deception_detector.clear_all()

        print(f"Session {self.session_id} shutdown complete")

    def get_performance_metrics(self):
        """Get current performance metrics."""
        if self.performance:
            return self.performance.get_metrics()
        return None
