"""Main application entry point."""

import sys
import yaml
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def load_config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Using default configuration")
        return get_default_config()


def get_default_config():
    """Get default configuration if config file not found."""
    return {
        'performance': {
            'initial_fps': 10,
            'min_fps': 5,
            'max_fps': 30,
            'adaptive': True,
            'target_cpu_percent': 70
        },
        'models': {
            'deepface': {'enabled': True, 'weight': 1.0, 'backend': 'opencv'},
            'fer': {'enabled': True, 'weight': 1.0},
            'mediapipe': {'enabled': True, 'weight': 1.0},
            'opencv': {'enabled': True, 'weight': 1.0}
        },
        'facs': {'enabled': False, 'deception_aus': [4, 15, 23, 24]},  # Disabled by default (py-feat optional)
        'ensemble': {'method': 'weighted_voting', 'min_models_required': 2},
        'deception': {
            'enabled': True,
            'confidence_threshold': 0.8,
            'microexpression_window_ms': 500,
            'suspicious_patterns': [
                ['fear', 'contempt'],
                ['disgust', 'happiness'],
                ['surprise', 'anger']
            ]
        },
        'screen_capture': {'monitor': 0, 'region': None},
        'ui': {
            'overlay': {
                'enabled': True,
                'visible_on_start': False,
                'bbox': {'color': [0, 255, 0], 'thickness': 2, 'deception_color': [255, 0, 0]},
                'label': {
                    'font_size': 12,
                    'background_opacity': 0.7,
                    'show_confidence': True,
                    'show_emotion': True
                }
            },
            'hotkeys': {
                'toggle_overlay': 'Ctrl+Shift+O',
                'toggle_monitoring': 'Ctrl+Shift+M'
            }
        },
        'logging': {
            'enabled': True,
            'directory': 'sessions',
            'format': 'json',
            'encrypt': True,
            'log_emotions': True,
            'log_confidence': True,
            'log_aus': True,
            'log_deception_events': True,
            'log_fps': True,
            'autosave_interval': 60
        }
    }


def main():
    """Main application entry point."""
    print("="*60)
    print("Facial Detection & Emotion Analysis System")
    print("="*60)
    print()

    # Load configuration
    config = load_config()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Facial Detection")

    # Create and show main window
    window = MainWindow(config)
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
