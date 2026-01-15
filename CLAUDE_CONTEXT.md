# Claude AI Agent Context

This document provides context for AI agents continuing work on this project.

## Project Status

**Status**: Core implementation complete, ready for testing and refinement

**Completed**:
- ✅ Full project structure and architecture
- ✅ Screen capture system (cross-platform with MSS)
- ✅ Face detection (OpenCV + MediaPipe)
- ✅ 4 emotion detection models (DeepFace, FER, MediaPipe, OpenCV)
- ✅ FACS Action Unit analysis (py-feat)
- ✅ Microexpression detection
- ✅ Deception detection system
- ✅ Ensemble voting for multi-model predictions
- ✅ PyQt6 UI with transparent overlay
- ✅ Adaptive performance monitoring
- ✅ Session logging with encryption
- ✅ Comprehensive unit tests
- ✅ Visual test page (emotion_test_page.html)
- ✅ Full documentation

**Next Steps**:
1. Install dependencies and run the application
2. Execute tests to verify all components work
3. Use emotion_test_page.html to validate detection accuracy
4. Test scrolling and face tracking
5. Verify session logs are created and encrypted
6. Performance tuning if needed

## Architecture Overview

### Data Flow
```
Screen Capture → Face Detection → Emotion Analysis → Deception Detection → UI Update → Session Logging
```

### Key Components

1. **SessionManager** (`src/core/session_manager.py`)
   - Orchestrates all components
   - Manages application lifecycle
   - Coordinates frame processing

2. **EmotionDetector** (`src/detection/emotion_detector.py`)
   - Initializes all ML models
   - Coordinates multi-model predictions
   - Uses ensemble voting for final decision

3. **DeceptionDetector** (`src/detection/deception.py`)
   - Analyzes FACS Action Units
   - Detects microexpressions
   - Checks suspicious emotion patterns
   - Evaluates model disagreement

4. **PerformanceMonitor** (`src/utils/performance.py`)
   - Tracks processing time
   - Adapts frame rate dynamically
   - Monitors CPU/memory usage

5. **TransparentOverlay** (`src/ui/overlay.py`)
   - Displays detection results
   - Shows bounding boxes and labels
   - Highlights deception alerts

### Configuration System

All configuration in `config/settings.yaml`:
- Performance parameters (FPS, CPU limits)
- Model enable/disable switches and weights
- FACS deception AUs
- Ensemble voting method
- UI styling
- Logging preferences

Can be modified without code changes.

## Testing Strategy

### 1. Unit Tests (`tests/unit/`)
Test individual components:
- Ensemble voting logic
- Data model conversions
- Validation functions
- Performance monitoring
- Microexpression detection

Run with: `pytest tests/unit/ -v`

### 2. Integration Tests (`tests/integration/`)
Test component interactions:
- End-to-end emotion detection pipeline
- Session management
- UI integration

Run with: `pytest tests/integration/ -v`

### 3. Visual Testing
Use `tests/emotion_test_page.html`:
1. Open in browser (full screen recommended)
2. Start application and enable monitoring
3. Verify each of 8 emotions detected correctly
4. Scroll to test face tracking
5. Check deception alerts on contempt images

### 4. Performance Testing
Monitor during extended use:
- FPS should stabilize at 5-10
- CPU usage should stay under 80%
- Memory usage should be stable (no leaks)
- No frame drops or lag

## Common Issues & Solutions

### Issue: Model initialization fails

**Cause**: Missing dependencies or incompatible versions

**Solution**:
```bash
pip install --upgrade -r requirements.txt
```

### Issue: py-feat fails to initialize

**Cause**: py-feat has complex dependencies

**Solution**: FACS is optional, set `facs.enabled: false` in config

### Issue: Low FPS

**Cause**: Too many models or system overload

**Solutions**:
- Disable models in config (keep 2-3 enabled)
- Lower `max_fps` in config
- Set `adaptive: true` for auto-adjustment

### Issue: Faces not detected

**Causes**: Screen capture permissions, poor image quality

**Solutions**:
- Grant screen recording permissions (macOS)
- Use better quality test images
- Try `method: "both"` in FaceDetector

### Issue: Inaccurate emotion detection

**Cause**: Single model may be unreliable

**Solution**: Ensemble voting helps - ensure multiple models enabled

### Issue: No deception alerts

**Causes**: Threshold too high, FACS disabled

**Solutions**:
- Lower `deception.confidence_threshold` (try 0.6-0.7)
- Enable FACS if disabled
- Check deception_aus list is correct

## Code Patterns

### Adding a New Feature

1. **Create module** in appropriate directory (core/models/detection/ui)
2. **Update __init__.py** to export new classes
3. **Add configuration** to settings.yaml
4. **Write tests** in tests/unit/
5. **Update documentation** in README.md and .clinerules

### Modifying Existing Logic

1. **Read tests first** to understand expected behavior
2. **Make changes** in source file
3. **Update tests** if behavior changed
4. **Run test suite** to ensure nothing broke
5. **Update docs** if user-facing changes

### Debugging

1. **Enable verbose logging** in code (print statements or logging module)
2. **Check session logs** in `sessions/` directory
3. **Use pytest -v** for detailed test output
4. **Monitor performance metrics** in UI

## Important Notes

### Model Characteristics

1. **DeepFace**: Most accurate, slowest, uses deep learning
2. **FER**: Fast, good balance of speed/accuracy
3. **MediaPipe**: Fast, heuristic-based, provides landmarks
4. **OpenCV**: Lightweight fallback, basic detection

### Deception Detection

Not 100% accurate - uses multiple signals:
- FACS AUs (4, 15, 23, 24 most indicative)
- Microexpressions (<500ms emotion changes)
- Suspicious emotion patterns
- Model disagreement (suppressed emotion)

Combine all for best results. Threshold adjustable in config.

### Performance Optimization

Bottlenecks (in order):
1. ML model inference (biggest)
2. Screen capture
3. Face detection
4. UI rendering

To optimize:
- Reduce number of active models
- Lower frame rate
- Disable FACS (heavy computation)
- Use simpler face detection method

## Project Goals

**Primary**: Educational and business use for deception detection in meetings/interviews

**Secondary**: Research tool for emotion analysis and FACS studies

**Key Requirements**:
- Real-time performance (5-10 FPS minimum)
- High accuracy (multi-model ensemble)
- Privacy (local processing, encryption)
- Cross-platform (Windows, macOS, Linux)
- User-friendly (simple UI, hotkeys)

## Future Enhancements

Potential additions:
- [ ] Real-time video recording with annotations
- [ ] Statistical analysis and reports
- [ ] Custom model training
- [ ] Multiple monitor support
- [ ] Remote monitoring (with consent)
- [ ] Integration with video conferencing apps
- [ ] Machine learning for personalized deception detection
- [ ] Export to various formats (CSV, PDF reports)

## Resources

- **DeepFace**: https://github.com/serengil/deepface
- **MediaPipe**: https://google.github.io/mediapipe/
- **py-feat**: https://py-feat.org/
- **PyQt6**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **FACS**: https://en.wikipedia.org/wiki/Facial_Action_Coding_System

## Questions to Ask User

When uncertain:
1. Which emotion detection is incorrect? (for tuning)
2. What FPS are you getting? (for performance)
3. Are deception alerts too frequent/rare? (for threshold tuning)
4. Which platform are you on? (for platform-specific issues)
5. What's the use case? (for feature prioritization)

## Final Notes

This is a complex ML application with many moving parts. When making changes:
- Test thoroughly
- Consider performance impact
- Update documentation
- Preserve existing functionality
- Ask user if uncertain about requirements

The application is designed to be modular and extensible. Most customization can be done through config/settings.yaml without code changes.
