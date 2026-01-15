"""Input validation utilities."""

import numpy as np
from typing import Optional, Tuple


def validate_frame(frame: np.ndarray) -> bool:
    """
    Validate that frame is a valid image array.

    Args:
        frame: Image array to validate

    Returns:
        True if valid, False otherwise
    """
    if frame is None:
        return False

    if not isinstance(frame, np.ndarray):
        return False

    # Check dimensions (should be 2D or 3D)
    if len(frame.shape) not in [2, 3]:
        return False

    # Check if not empty
    if frame.size == 0:
        return False

    return True


def validate_face_region(
    x: int, y: int, w: int, h: int,
    frame_width: int, frame_height: int
) -> bool:
    """
    Validate that face region is within frame bounds.

    Args:
        x, y: Top-left coordinates
        w, h: Width and height
        frame_width, frame_height: Frame dimensions

    Returns:
        True if valid, False otherwise
    """
    if x < 0 or y < 0 or w <= 0 or h <= 0:
        return False

    if x + w > frame_width or y + h > frame_height:
        return False

    return True


def validate_confidence(confidence: float) -> bool:
    """
    Validate confidence score is in valid range.

    Args:
        confidence: Confidence value to validate

    Returns:
        True if valid (0.0 to 1.0), False otherwise
    """
    return 0.0 <= confidence <= 1.0


def normalize_confidence(confidence: float) -> float:
    """
    Normalize confidence to 0.0-1.0 range.

    Args:
        confidence: Raw confidence value

    Returns:
        Normalized confidence
    """
    return max(0.0, min(1.0, confidence))


def validate_emotion(emotion: str, valid_emotions: list) -> bool:
    """
    Validate that emotion is in the list of valid emotions.

    Args:
        emotion: Emotion string to validate
        valid_emotions: List of valid emotion labels

    Returns:
        True if valid, False otherwise
    """
    return emotion.lower() in [e.lower() for e in valid_emotions]
