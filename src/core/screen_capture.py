"""Screen capture functionality for cross-platform monitoring."""

import numpy as np
import mss
import mss.tools
from typing import Optional, Tuple
import cv2


class ScreenCapture:
    """Captures screen content for face detection."""

    def __init__(self, monitor_index: int = 0, region: Optional[Tuple[int, int, int, int]] = None):
        """
        Initialize screen capture.

        Args:
            monitor_index: Monitor to capture (0 = primary, 1 = secondary, etc.)
            region: Optional region to capture as (x, y, width, height). None = full screen
        """
        self.sct = mss.mss()
        self.monitor_index = monitor_index
        self.region = region

        # Get monitor info
        self.monitors = self.sct.monitors
        # monitors[0] is all monitors combined, monitors[1+] are individual monitors
        actual_index = monitor_index + 1
        if actual_index >= len(self.monitors):
            # Fallback to all monitors if requested index doesn't exist
            actual_index = 0

        self.monitor = self.monitors[actual_index]

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the screen.

        Returns:
            Frame as numpy array (BGR format) or None if capture fails
        """
        try:
            # Determine capture region
            if self.region:
                x, y, w, h = self.region
                capture_area = {"left": x, "top": y, "width": w, "height": h}
            else:
                capture_area = self.monitor

            # Capture screen
            screenshot = self.sct.grab(capture_area)

            # Convert to numpy array
            frame = np.array(screenshot)

            # Convert BGRA to BGR (remove alpha channel)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            return frame

        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def get_screen_dimensions(self) -> Tuple[int, int]:
        """
        Get dimensions of the capture area.

        Returns:
            (width, height) tuple
        """
        if self.region:
            return (self.region[2], self.region[3])
        else:
            return (self.monitor["width"], self.monitor["height"])

    def set_region(self, region: Optional[Tuple[int, int, int, int]]) -> None:
        """
        Update capture region.

        Args:
            region: New region as (x, y, width, height) or None for full screen
        """
        self.region = region

    def close(self) -> None:
        """Release screen capture resources."""
        if self.sct:
            self.sct.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
