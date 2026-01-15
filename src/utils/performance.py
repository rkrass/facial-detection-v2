"""Performance monitoring and adaptive frame rate management."""

import time
import psutil
from typing import Optional
from ..data.models import PerformanceMetrics


class PerformanceMonitor:
    """Monitors system performance and adjusts frame rate adaptively."""

    def __init__(
        self,
        initial_fps: int = 10,
        min_fps: int = 5,
        max_fps: int = 30,
        target_cpu_percent: float = 70.0
    ):
        self.initial_fps = initial_fps
        self.min_fps = min_fps
        self.max_fps = max_fps
        self.target_cpu_percent = target_cpu_percent

        self.current_fps = initial_fps
        self.frame_times = []
        self.max_frame_time_samples = 30

        self.process = psutil.Process()
        self.dropped_frames = 0

    def record_frame_time(self, processing_time: float) -> None:
        """Record processing time for a frame."""
        self.frame_times.append(processing_time)
        if len(self.frame_times) > self.max_frame_time_samples:
            self.frame_times.pop(0)

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        cpu_percent = self.process.cpu_percent()
        memory_mb = self.process.memory_info().rss / 1024 / 1024

        return PerformanceMetrics(
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            current_fps=self.current_fps,
            target_fps=self.target_fps,
            dropped_frames=self.dropped_frames
        )

    def adapt_frame_rate(self) -> int:
        """
        Adjust frame rate based on system performance.

        Returns:
            New target FPS
        """
        if not self.frame_times:
            return self.current_fps

        # Get average processing time
        avg_time = sum(self.frame_times) / len(self.frame_times)
        cpu_percent = self.process.cpu_percent()

        # Calculate theoretical max FPS based on processing time
        if avg_time > 0:
            theoretical_fps = 1.0 / avg_time
        else:
            theoretical_fps = self.max_fps

        # Adjust based on CPU usage
        if cpu_percent > self.target_cpu_percent:
            # Reduce FPS
            new_fps = max(self.min_fps, self.current_fps - 1)
        elif cpu_percent < self.target_cpu_percent * 0.7 and theoretical_fps > self.current_fps:
            # Increase FPS if we have headroom
            new_fps = min(self.max_fps, self.current_fps + 1)
        else:
            new_fps = self.current_fps

        # Ensure we don't exceed theoretical limit
        new_fps = min(new_fps, int(theoretical_fps * 0.9))

        self.current_fps = new_fps
        return new_fps

    @property
    def target_fps(self) -> int:
        """Get target FPS."""
        return self.current_fps

    @property
    def frame_interval(self) -> float:
        """Get time between frames in seconds."""
        return 1.0 / self.current_fps if self.current_fps > 0 else 0.1

    def should_process_frame(self, last_process_time: float) -> bool:
        """
        Determine if enough time has passed to process next frame.

        Args:
            last_process_time: Timestamp of last processed frame

        Returns:
            True if frame should be processed
        """
        current_time = time.time()
        elapsed = current_time - last_process_time

        if elapsed >= self.frame_interval:
            return True
        else:
            return False

    def mark_dropped_frame(self) -> None:
        """Increment dropped frame counter."""
        self.dropped_frames += 1
