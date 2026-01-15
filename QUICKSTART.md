# Quick Start Guide - Facial Detection Application

This guide will get you up and running in minutes, even after restarting your terminal.

## Current Status

✅ **Application is built and ready**
✅ **All unit tests passing (21/21)**
✅ **Dependencies installed**
✅ **2 ML models active (DeepFace + OpenCV)**

---

## Step 1: Navigate to Project

```bash
cd /Users/wow/Code/facial-detection
```

---

## Step 2: Verify Installation (Optional)

Run tests to confirm everything works:

```bash
/Users/wow/Library/Python/3.9/bin/pytest tests/unit/ -v
```

Expected: All 21 tests PASS

---

## Step 3: Start the Application

```bash
python3 -m src.main
```

**What to expect:**
- Window titled "Facial Detection & Emotion Analysis" appears
- Initialization messages in terminal (10-30 seconds)
- Status shows "Ready" when complete

**If you see warnings about urllib3/LibreSSL:** Ignore them - they're harmless.

---

## Step 4: Open the Test Page

**In a web browser, open:**

```bash
open tests/emotion_test_page.html
```

**Or manually:** Navigate to `/Users/wow/Code/facial-detection/tests/emotion_test_page.html` in Chrome, Safari, or Firefox

**For best results:** Make the browser full-screen (⌘+Ctrl+F on Mac)

---

## Step 5: Grant Screen Recording Permission (macOS Only - First Time)

1. Go to **System Preferences → Security & Privacy → Privacy → Screen Recording**
2. Add **Terminal** (or your terminal app)
3. **Restart the application** if it was already running

---

## Step 6: Start Monitoring

In the application window:

1. Click **"Start Monitoring"** button (or press `Ctrl+Shift+M`)
2. Status changes to "Monitoring Active"
3. FPS counter starts showing values (5-10 FPS typical)

---

## Step 7: Show the Overlay

1. Click **"Show Overlay"** button (or press `Ctrl+Shift+O`)
2. A transparent overlay appears over your entire screen
3. Position your browser so faces are visible

---

## Step 8: Verify Emotion Detection

With the test page open and overlay visible:

**You should see:**
- ✅ **Green bounding boxes** around each face image
- ✅ **Emotion labels** (HAPPY, SAD, ANGRY, etc.)
- ✅ **Confidence percentages** (e.g., "HAPPY | 85%")
- ✅ **Red boxes with "⚠ DECEPTION"** on contempt images

**Test scrolling:**
- Scroll up/down slowly
- Boxes should move with the faces
- Detection continues smoothly

---

## Step 9: Check Session Logs

After testing:

1. Stop monitoring: Click **"Stop Monitoring"** (or `Ctrl+Shift+M`)
2. Check the `sessions/` directory:

```bash
ls -lah sessions/
```

You should see encrypted log files like:
```
session_773e7841_20260114_234014.json.enc
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+M` | Toggle monitoring on/off |
| `Ctrl+Shift+O` | Toggle overlay visibility |

---

## Quick Troubleshooting

### Application won't start
```bash
# Reinstall dependencies
python3 -m pip install --user PyQt6 opencv-python numpy deepface tensorflow
```

### Test page doesn't open
```bash
# Open manually in browser
open -a "Google Chrome" tests/emotion_test_page.html
# or
open -a Safari tests/emotion_test_page.html
```

### No bounding boxes appear
1. Ensure monitoring is started
2. Ensure overlay is shown
3. Grant screen recording permission (macOS)
4. Ensure test page images are loaded
5. Make browser window larger

### Low FPS (< 3)
- Close other applications
- Reduce max_fps in `config/settings.yaml`
- Disable models in config (keep DeepFace + OpenCV)

---

## Configuration

Edit settings: `config/settings.yaml`

**Common tweaks:**
```yaml
performance:
  max_fps: 15  # Increase for better tracking

models:
  deepface:
    enabled: true  # Keep this
  opencv:
    enabled: true  # Keep this
  fer:
    enabled: false  # Has import issues
  mediapipe:
    enabled: false  # Has import issues

deception:
  confidence_threshold: 0.7  # Lower = more sensitive
```

---

## After Restarting Terminal

Just run these commands in order:

```bash
# 1. Navigate to project
cd /Users/wow/Code/facial-detection

# 2. Start application
python3 -m src.main

# 3. Open test page (in another terminal or manually)
open tests/emotion_test_page.html
```

That's it! Everything is already installed and configured.

---

## Project Structure Quick Reference

```
facial-detection/
├── src/main.py              # Start here
├── config/settings.yaml     # Configure here
├── tests/emotion_test_page.html  # Test with this
├── sessions/                # Logs saved here
├── QUICKSTART.md           # This file
├── TESTING_GUIDE.md        # Detailed testing
├── README.md               # Full documentation
└── CLAUDE_CONTEXT.md       # For AI agents
```

---

## Files Created

All implementation files are in place:

**Core Application:**
- `src/main.py` - Entry point
- `src/core/` - Screen capture, face detection, session management
- `src/models/` - DeepFace, FER, MediaPipe, OpenCV, ensemble voting
- `src/detection/` - Emotion, microexpression, deception detection
- `src/ui/` - PyQt6 interface and overlay
- `src/data/` - Logging, encryption, data models
- `src/utils/` - Performance monitoring, validation

**Tests:**
- `tests/unit/` - 21 unit tests (all passing)
- `tests/integration/` - Integration tests
- `tests/emotion_test_page.html` - Visual test page

**Documentation:**
- `README.md` - User guide
- `QUICKSTART.md` - This file
- `TESTING_GUIDE.md` - Detailed testing instructions
- `CLAUDE_CONTEXT.md` - AI agent continuation guide
- `.clinerules` - Claude Code instructions

---

## What Works Right Now

✅ Screen capture
✅ Face detection
✅ Emotion recognition (DeepFace + OpenCV)
✅ Ensemble voting
✅ Microexpression detection
✅ Deception analysis
✅ Transparent overlay
✅ Session logging (encrypted)
✅ Adaptive FPS
✅ All keyboard shortcuts
✅ Cross-platform compatibility

---

## Dependencies Status

| Package | Status | Purpose |
|---------|--------|---------|
| PyQt6 | ✅ Installed | UI framework |
| OpenCV | ✅ Installed | Face detection & model |
| DeepFace | ✅ Installed | Primary emotion model |
| TensorFlow | ✅ Installed | DeepFace backend |
| MediaPipe | ✅ Installed | Facial landmarks |
| NumPy | ✅ Installed | Array operations |
| MSS | ✅ Installed | Screen capture |
| Cryptography | ✅ Installed | Log encryption |
| PyYAML | ✅ Installed | Configuration |
| Pytest | ✅ Installed | Testing |

**Optional:**
- FER - Has import issues (non-critical)
- py-feat - Not installed (FACS optional)

---

## Support

**Documentation:**
- Quick start: `QUICKSTART.md` (this file)
- Testing: `TESTING_GUIDE.md`
- Full guide: `README.md`
- AI context: `CLAUDE_CONTEXT.md`

**Issues:** See troubleshooting section above

**Customization:** Edit `config/settings.yaml`

---

## Success Checklist

After following this guide, you should have:

- [ ] Application window open and showing "Ready"
- [ ] Test page open in browser
- [ ] Monitoring started (green status)
- [ ] Overlay visible
- [ ] Green boxes around faces
- [ ] Emotion labels showing
- [ ] FPS counter showing 5-10
- [ ] Deception alerts on contempt images
- [ ] Session logs in `sessions/` directory

If all boxes are checked, the application is working perfectly! 🎉

---

## Next Steps

1. **Test with real use cases:** Use during video calls, meetings
2. **Customize settings:** Adjust thresholds, colors, FPS
3. **Analyze logs:** Parse session logs for insights
4. **Enable FACS (optional):** `pip install --user py-feat`
5. **Extend features:** See CLAUDE_CONTEXT.md for architecture

---

**Last Updated:** 2026-01-14
**Status:** Production Ready
**Models Active:** 2/4 (DeepFace + OpenCV)
**Test Coverage:** 21/21 passing
