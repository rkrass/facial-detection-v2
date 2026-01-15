# Testing Guide

This guide will help you verify that the Facial Detection & Emotion Analysis application is working correctly.

## Prerequisites

All dependencies have been installed. If you need to reinstall:

```bash
python3 -m pip install --user PyQt6 opencv-python numpy mss PyYAML cryptography psutil Pillow mediapipe tensorflow tf-keras deepface fer pytest pytest-mock
```

## Step 1: Run Unit Tests

First, verify that all core functionality works:

```bash
/Users/wow/Library/Python/3.9/bin/pytest tests/unit/ -v
```

**Expected Result**: All 21 tests should PASS

## Step 2: Start the Application

Launch the main application:

```bash
cd /Users/wow/Code/facial-detection
python3 -m src.main
```

**Expected Result**: A window titled "Facial Detection & Emotion Analysis" should appear

**If you see warnings about urllib3/LibreSSL**: These are harmless and can be ignored.

## Step 3: Grant Screen Recording Permission (macOS only)

On macOS, you'll need to grant screen recording permission:

1. Go to System Preferences → Security & Privacy → Privacy → Screen Recording
2. Add Terminal (or your terminal app) to the allowed apps
3. Restart the application if needed

## Step 4: Initialize the System

In the application window:

1. Wait for "Ready" status to appear (may take 10-30 seconds for models to initialize)
2. Check the event log for:
   - "✓ Screen capture initialized"
   - "✓ Face detector initialized"
   - "✓ DeepFace model initialized"
   - "✓ FER model initialized"
   - "✓ MediaPipe model initialized"
   - "✓ OpenCV model initialized"

**Note**: py-feat (FACS) is disabled by default. If you want to enable it:
```bash
python3 -m pip install --user py-feat
```
Then set `facs.enabled: true` in `config/settings.yaml`

## Step 5: Open the Test Page

Open the emotion test page in your web browser:

```bash
open tests/emotion_test_page.html
```

Or manually open the file in any browser (Chrome, Firefox, Safari).

**Pro Tip**: Use full-screen mode (F11 or Cmd+Ctrl+F) for best results.

## Step 6: Start Monitoring

Back in the application:

1. Click "Start Monitoring" (or press `Ctrl+Shift+M`)
2. Status should change to "Monitoring Active"
3. FPS counter should start showing values (typically 5-10 FPS)

## Step 7: Enable the Overlay

To see detection results overlaid on your screen:

1. Click "Show Overlay" (or press `Ctrl+Shift+O`)
2. A transparent overlay will appear over your entire screen
3. This overlay will show bounding boxes and emotion labels

## Step 8: Verify Emotion Detection

With the test page open and overlay visible:

1. **Happy Face**: Should show green box with "HAPPY | 70-90%"
2. **Sad Face**: Should show green box with "SAD | 70-90%"
3. **Angry Face**: Should show "ANGRY"
4. **Disgust Face**: Should show "DISGUST"
5. **Fear Face**: Should show "FEAR"
6. **Surprise Face**: Should show "SURPRISE"
7. **Neutral Face**: Should show "NEUTRAL"
8. **Contempt Face**: May trigger ⚠ DECEPTION alert (red box)

**What to Look For**:
- ✅ Bounding boxes appear around each face
- ✅ Emotion labels are correct (or close - some variations are normal)
- ✅ Confidence scores are above 60% for clear emotions
- ✅ Labels update smoothly as you scroll

## Step 9: Test Scrolling and Tracking

1. Slowly scroll up and down the test page
2. Verify that:
   - Bounding boxes move with the faces
   - Detection continues as faces move
   - No significant lag or stuttering
   - FPS remains stable

## Step 10: Test Deception Detection

Scroll to the "Contempt" emotion card:

1. Check if a deception alert appears
2. Look in the Event Log for messages like:
   - "⚠ DECEPTION DETECTED - Face 0: Microexpression detected..."
   - "⚠ DECEPTION DETECTED - Face 0: Suspicious emotion sequence..."

**Note**: Deception detection is heuristic and not always triggered. This is expected behavior.

## Step 11: Check Session Logs

After testing:

1. Stop monitoring (click "Stop Monitoring" or press `Ctrl+Shift+M`)
2. Check the `sessions/` directory:
   ```bash
   ls -lah sessions/
   ```
3. You should see a file like `session_XXXXXXXX_YYYYMMDD_HHMMSS.json.enc`
4. This contains encrypted logs of all detections

## Step 12: Performance Verification

During monitoring, verify:

- **FPS**: Should be 5-10 FPS (adaptive, will adjust based on system load)
- **CPU Usage**: Should be < 80% (check Activity Monitor/Task Manager)
- **Memory**: Should be stable, not continuously increasing
- **Responsiveness**: UI should remain responsive, no freezing

## Troubleshooting

### Models Don't Initialize

**Problem**: "ERROR: No emotion models were initialized!"

**Solution**:
```bash
python3 -m pip install --user deepface fer mediapipe tensorflow tf-keras
```

### Low FPS (< 3 FPS)

**Problem**: System is slow, FPS very low

**Solutions**:
1. Disable some models in `config/settings.yaml` (keep 2-3 enabled)
2. Lower `max_fps` to 5 in config
3. Close other applications

### Faces Not Detected

**Problem**: No bounding boxes appear

**Solutions**:
1. Ensure test page images are fully loaded
2. Check screen capture permissions (macOS)
3. Make browser window large enough
4. Try different test images

### Overlay Not Visible

**Problem**: Pressed Ctrl+Shift+O but nothing appears

**Solutions**:
1. Check if overlay is behind other windows (it should be on top)
2. Restart the application
3. Verify monitoring is active first

### Inaccurate Emotion Detection

**Problem**: Emotions are often wrong

**Expected**: Some inaccuracy is normal, especially with test images from the web. Multi-model ensemble helps but isn't perfect.

**To Improve**:
1. Ensure all 4 models are initialized
2. Use higher quality test images
3. Adjust model weights in config
4. Try your own face via webcam (requires code modification)

## Advanced Testing

### Test with Real Faces

If you have a webcam, you can modify `src/core/screen_capture.py` to capture from webcam instead of screen. This will give more accurate results with real facial expressions.

### Test Session Log Decryption

To verify encryption works:

```python
from src.data.logger import SessionLogger
from src.main import load_config

config = load_config()
logger = SessionLogger(config)

# Load and decrypt a session
data = logger.load_session('sessions/session_XXXXXXXX.json.enc')
print(data)
```

### Stress Test

Leave monitoring running for 5-10 minutes and verify:
- No memory leaks (memory usage stable)
- No crashes
- FPS remains consistent
- Session logs are periodically saved

## Success Criteria

The application is working correctly if:

- ✅ All 21 unit tests pass
- ✅ Application starts without errors
- ✅ At least 2 emotion models initialize successfully
- ✅ Faces are detected on the test page
- ✅ Emotion labels are mostly accurate (>60% correct)
- ✅ Overlay displays correctly
- ✅ Scrolling tracking works
- ✅ FPS is stable at 5-10
- ✅ Session logs are created
- ✅ No crashes during 5+ minute test

## Next Steps

Once testing is complete:

1. **Customize Configuration**: Edit `config/settings.yaml` to tune performance, model weights, deception thresholds
2. **Enable FACS**: Install py-feat if you want Action Unit analysis
3. **Add Custom Models**: Add your own emotion recognition models in `src/models/`
4. **Integrate with Tools**: Use the application during video calls, meetings, etc.
5. **Analyze Logs**: Write scripts to parse session logs and generate reports

## Questions?

See:
- `README.md` for general information
- `CLAUDE_CONTEXT.md` for architectural details
- `.clinerules` for code modification guidelines
- Source code comments for implementation details
