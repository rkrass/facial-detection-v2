# Facial Detection & Emotion Analysis System

A cross-platform desktop application for real-time facial detection, emotion recognition, and deception analysis using multiple ML models.

## Features

- **Real-Time Face Detection**: Monitors your screen and detects faces in real-time
- **Multi-Model Emotion Recognition**: Uses 4 different ML models (DeepFace, FER, MediaPipe, OpenCV) with ensemble voting for accurate results
- **FACS Action Unit Detection**: Analyzes facial Action Units using py-feat
- **Microexpression Detection**: Captures brief involuntary facial expressions
- **Deception Detection**: Identifies potential deception through facial cues, microexpressions, and FACS AUs
- **Transparent Overlay**: Toggle-able overlay showing detection results
- **Adaptive Performance**: Automatically adjusts frame rate based on system resources
- **Session Logging**: Encrypted logs of all detections with timestamps
- **Configurable**: Extensive YAML configuration for all parameters

## Installation

### Prerequisites
- Python 3.8 or higher
- pip
- Sufficient RAM (4GB+ recommended)
- CPU/GPU for ML model inference

### Setup

1. **Clone or navigate to the project**:
```bash
cd /Users/wow/Code/facial-detection
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
python -m src.main
```

## Usage

### Starting the Application

1. Launch the application:
```bash
python -m src.main
```

2. Click "Start Monitoring" or press `Ctrl+Shift+M`

3. Toggle the overlay with "Show Overlay" button or press `Ctrl+Shift+O`

4. The application will detect faces and emotions in real-time

### Hotkeys

- `Ctrl+Shift+M`: Toggle monitoring on/off
- `Ctrl+Shift+O`: Toggle overlay visibility

### Testing Emotion Detection

1. Start the application
2. Open `tests/emotion_test_page.html` in your web browser
3. Position the browser window where the application can see it
4. Enable monitoring and overlay
5. Scroll through the different emotion images to verify detection accuracy

## Configuration

Edit `config/settings.yaml` to customize:

- **Performance**: FPS limits, adaptive mode, CPU targets
- **Models**: Enable/disable specific models, adjust weights
- **FACS**: Action Units for deception detection
- **Deception**: Confidence thresholds, suspicious patterns
- **UI**: Overlay colors, fonts, hotkeys
- **Logging**: Session logs, encryption, what to log

## Project Structure

```
facial-detection/
├── config/
│   └── settings.yaml          # Configuration file
├── src/
│   ├── main.py               # Application entry point
│   ├── core/                 # Core components
│   │   ├── screen_capture.py
│   │   ├── face_detector.py
│   │   └── session_manager.py
│   ├── models/               # ML model wrappers
│   │   ├── base_model.py
│   │   ├── deepface_model.py
│   │   ├── fer_model.py
│   │   ├── mediapipe_model.py
│   │   ├── opencv_model.py
│   │   ├── facs_analyzer.py
│   │   └── ensemble.py
│   ├── detection/            # Detection logic
│   │   ├── emotion_detector.py
│   │   ├── microexpression.py
│   │   └── deception.py
│   ├── ui/                   # User interface
│   │   ├── main_window.py
│   │   └── overlay.py
│   ├── data/                 # Data models
│   │   ├── models.py
│   │   ├── logger.py
│   │   └── encryption.py
│   └── utils/                # Utilities
│       ├── performance.py
│       └── validators.py
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── emotion_test_page.html  # Visual testing page
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Adding a New Emotion Model

1. Create a new file in `src/models/` inheriting from `BaseEmotionModel`
2. Implement required methods: `initialize()`, `predict_emotion()`, `get_supported_emotions()`
3. Add the model to `EmotionDetector` in `src/detection/emotion_detector.py`
4. Update `config/settings.yaml` with model configuration
5. Add unit tests in `tests/unit/test_models.py`

## Use Cases

- **Educational**: Learn about emotion detection and computer vision
- **Research**: Collect data on emotional responses
- **Business**: Detect potential deception in meetings, negotiations, interviews
- **Personal**: Track your own emotional states during work or gaming

## Privacy & Ethics

- **Local Processing**: All face and emotion data is processed locally, never sent to the cloud
- **Encrypted Logs**: Session logs are encrypted using AES-256
- **User Control**: Toggle monitoring and overlay visibility at any time
- **Ethical Use**: Intended for authorized use only (consent required when monitoring others)

## Troubleshooting

### Models fail to initialize
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Some models require additional system libraries (e.g., OpenCV)

### Low FPS / Poor Performance
- Disable some models in `config/settings.yaml`
- Reduce `max_fps` in configuration
- Close other resource-intensive applications

### Faces not detected
- Ensure screen capture has proper permissions
- Try changing `face_detector` method in code (opencv/mediapipe/both)
- Check lighting conditions in test images

### Overlay not visible
- Press `Ctrl+Shift+O` to toggle
- Check if overlay is behind other windows
- Verify overlay is enabled in config

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is for educational and research purposes.

## Acknowledgments

- DeepFace for emotion detection models
- MediaPipe for facial landmark detection
- py-feat for FACS Action Unit analysis
- FER library for emotion recognition
- OpenCV for computer vision operations
