# Complete File Index

**Everything that was created for this project.**

---

## 📖 Documentation (Read These)

| File | Purpose | When to Read |
|------|---------|--------------|
| **START_HERE.md** | First entry point | **READ FIRST** |
| **RESUME.md** | Quick resume after restart | After terminal restart |
| **QUICKSTART.md** | Detailed startup guide | First time using |
| **TESTING_GUIDE.md** | Complete testing instructions | When testing thoroughly |
| **README.md** | Full project documentation | For comprehensive understanding |
| **CLAUDE_CONTEXT.md** | AI agent continuation guide | For AI agents or developers |
| **.clinerules** | Claude Code instructions | When modifying code |
| **FILE_INDEX.md** | This file - complete file list | For navigation |

---

## 🚀 Executables

| File | Purpose | How to Use |
|------|---------|------------|
| **start.sh** | Application launcher | `./start.sh` |
| **src/main.py** | Application entry point | `python3 -m src.main` |

---

## ⚙️ Configuration

| File | Purpose | Format |
|------|---------|--------|
| **config/settings.yaml** | All application settings | YAML |
| **requirements.txt** | Python dependencies | Text |
| **setup.py** | Package installation | Python |
| **.gitignore** | Git ignore rules | Text |

---

## 🧪 Testing Files

### Test Code
| File | Purpose |
|------|---------|
| **tests/conftest.py** | Pytest fixtures and configuration |
| **tests/unit/test_models.py** | Ensemble voting and data model tests |
| **tests/unit/test_utils.py** | Validation and performance tests |
| **tests/unit/test_detection.py** | Microexpression and deception tests |
| **tests/integration/test_pipeline.py** | Full pipeline integration tests |

### Visual Testing
| File | Purpose | How to Use |
|------|---------|------------|
| **tests/emotion_test_page.html** | Visual emotion detection test page | Open in browser |

**Location:** `/Users/wow/Code/facial-detection/tests/emotion_test_page.html`

**To open:**
```bash
open tests/emotion_test_page.html
# Or
open -a "Google Chrome" tests/emotion_test_page.html
```

---

## 💻 Source Code

### Entry Point
- **src/main.py** - Application launcher, config loader

### Core Components
- **src/core/screen_capture.py** - Screen capture using MSS
- **src/core/face_detector.py** - Face detection (OpenCV + MediaPipe)
- **src/core/session_manager.py** - Session lifecycle orchestration

### Emotion Models
- **src/models/base_model.py** - Abstract base class for all models
- **src/models/deepface_model.py** - DeepFace wrapper
- **src/models/fer_model.py** - FER wrapper
- **src/models/mediapipe_model.py** - MediaPipe landmark-based detection
- **src/models/opencv_model.py** - OpenCV heuristic detection
- **src/models/facs_analyzer.py** - FACS Action Unit detection (py-feat)
- **src/models/ensemble.py** - Multi-model voting system

### Detection Logic
- **src/detection/emotion_detector.py** - Emotion detection coordinator
- **src/detection/microexpression.py** - Microexpression detection (<500ms)
- **src/detection/deception.py** - Deception analysis (AUs, patterns, disagreement)

### User Interface
- **src/ui/main_window.py** - Main PyQt6 application window
- **src/ui/overlay.py** - Transparent overlay for display

### Data & Logging
- **src/data/models.py** - Data structures (FaceRegion, EmotionPrediction, etc.)
- **src/data/logger.py** - Session logging with encryption
- **src/data/encryption.py** - AES-256 encryption for logs

### Utilities
- **src/utils/performance.py** - Performance monitoring and adaptive FPS
- **src/utils/validators.py** - Input validation functions

### Init Files
- **src/__init__.py**
- **src/core/__init__.py**
- **src/models/__init__.py**
- **src/detection/__init__.py**
- **src/ui/__init__.py**
- **src/data/__init__.py**
- **src/utils/__init__.py**
- **tests/__init__.py**
- **tests/unit/__init__.py**
- **tests/integration/__init__.py**

---

## 📊 Statistics

**Total Files:** 45+
**Lines of Code:** 3,500+
**Documentation Files:** 8
**Test Files:** 5
**Source Files:** 25+

---

## 📁 Directory Structure

```
facial-detection/
│
├── 📖 Documentation
│   ├── START_HERE.md           ← Entry point
│   ├── RESUME.md               ← Quick resume
│   ├── QUICKSTART.md           ← Detailed startup
│   ├── TESTING_GUIDE.md        ← Testing instructions
│   ├── README.md               ← Full documentation
│   ├── CLAUDE_CONTEXT.md       ← AI continuation
│   ├── FILE_INDEX.md           ← This file
│   └── .clinerules             ← Code guidelines
│
├── 🚀 Executables
│   ├── start.sh                ← Launcher script
│   └── src/main.py             ← Application entry
│
├── ⚙️ Configuration
│   ├── config/
│   │   └── settings.yaml       ← All settings
│   ├── requirements.txt        ← Dependencies
│   ├── setup.py                ← Package setup
│   └── .gitignore              ← Git ignores
│
├── 💻 Source Code
│   └── src/
│       ├── main.py             ← Entry point
│       ├── core/               ← Screen, face, session
│       ├── models/             ← ML models
│       ├── detection/          ← Emotion, deception
│       ├── ui/                 ← PyQt6 interface
│       ├── data/               ← Data models, logging
│       └── utils/              ← Utilities
│
├── 🧪 Tests
│   └── tests/
│       ├── emotion_test_page.html  ← Visual test page
│       ├── conftest.py             ← Pytest config
│       ├── unit/                   ← Unit tests (21)
│       └── integration/            ← Integration tests
│
└── 📦 Generated (Created at Runtime)
    └── sessions/               ← Encrypted session logs
        └── session_*.json.enc  ← Individual session files
```

---

## 🔍 File Locations

### To Find the Test Page:
```bash
/Users/wow/Code/facial-detection/tests/emotion_test_page.html
```

### To Find Config:
```bash
/Users/wow/Code/facial-detection/config/settings.yaml
```

### To Find Main Application:
```bash
/Users/wow/Code/facial-detection/src/main.py
```

### To Find Session Logs (After Use):
```bash
/Users/wow/Code/facial-detection/sessions/
```

---

## 🎯 Quick Navigation Commands

```bash
# Go to project root
cd /Users/wow/Code/facial-detection

# View all documentation
ls -lah *.md

# View source code structure
tree src/  # If tree is installed
# or
ls -R src/

# View tests
ls -lah tests/

# Open test page
open tests/emotion_test_page.html

# View config
cat config/settings.yaml

# Run tests
/Users/wow/Library/Python/3.9/bin/pytest tests/unit/ -v

# Start application
python3 -m src.main
# or
./start.sh
```

---

## 📝 File Purposes Quick Reference

**Want to:**
- **Start the app?** → Run `start.sh` or `src/main.py`
- **Test visually?** → Open `tests/emotion_test_page.html`
- **Configure?** → Edit `config/settings.yaml`
- **Resume after restart?** → Read `RESUME.md`
- **Understand architecture?** → Read `CLAUDE_CONTEXT.md`
- **Test code?** → Run `pytest tests/unit/`
- **Modify code?** → See `.clinerules`
- **View logs?** → Check `sessions/` directory

---

## ✅ Verification Checklist

All these files should exist:

**Documentation:**
- [x] START_HERE.md
- [x] RESUME.md
- [x] QUICKSTART.md
- [x] TESTING_GUIDE.md
- [x] README.md
- [x] CLAUDE_CONTEXT.md
- [x] FILE_INDEX.md
- [x] .clinerules

**Executables:**
- [x] start.sh
- [x] src/main.py

**Config:**
- [x] config/settings.yaml
- [x] requirements.txt
- [x] setup.py

**Tests:**
- [x] tests/emotion_test_page.html
- [x] tests/unit/test_models.py
- [x] tests/unit/test_utils.py
- [x] tests/unit/test_detection.py
- [x] tests/integration/test_pipeline.py

**Source (25+ files):**
- [x] All src/ modules implemented

---

**Total Implementation:** 100% Complete ✅
**All Files:** Created and Verified ✅
**Ready to Use:** Yes! 🚀
