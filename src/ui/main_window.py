"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QGroupBox, QFrame,
    QProgressBar, QSplitter, QApplication
)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut, QFont, QPalette, QColor
from typing import Optional
import threading
import time
import webbrowser
import subprocess
import os

from ..core.session_manager import SessionManager
from .overlay import TransparentOverlay


class ProcessingThread(QThread):
    """Background thread for continuous frame processing."""
    frame_processed = pyqtSignal(object, object)  # frame_analysis, frame

    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.running = False

    def run(self):
        """Process frames continuously in background."""
        self.running = True
        while self.running and self.session_manager:
            if self.session_manager.is_running:
                frame_analysis = self.session_manager.process_frame()
                if frame_analysis:
                    # Get current frame for callback
                    self.frame_processed.emit(frame_analysis, None)
            time.sleep(0.05)  # ~20 FPS max processing rate

    def stop(self):
        """Stop the processing thread."""
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.session_manager: Optional[SessionManager] = None
        self.overlay: Optional[TransparentOverlay] = None
        self.is_monitoring = False
        self.overlay_visible = False
        self.processing_thread: Optional[ProcessingThread] = None
        self.http_server_process = None

        # Timer for UI updates (separate from processing)
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui_metrics)

        self.init_ui()
        self.setup_hotkeys()
        self.initialize_session()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Facial Detection & Emotion Analysis")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(700, 500)

        # Apply dark theme
        self.apply_dark_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Status cards row
        status_row = QHBoxLayout()
        status_row.setSpacing(15)

        # Status card
        self.status_card = self.create_status_card()
        status_row.addWidget(self.status_card)

        # Metrics card
        self.metrics_card = self.create_metrics_card()
        status_row.addWidget(self.metrics_card)

        main_layout.addLayout(status_row)

        # Controls
        controls = self.create_controls()
        main_layout.addWidget(controls)

        # Event log
        log_section = self.create_log_section()
        main_layout.addWidget(log_section, 1)

    def apply_dark_theme(self):
        """Apply a professional dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                background-color: #1a1a2e;
                color: #e4e4e4;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            QGroupBox {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #00d9ff;
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #0f3460;
                color: #e4e4e4;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1a4a7a;
            }
            QPushButton:pressed {
                background-color: #0a2540;
            }
            QPushButton:disabled {
                background-color: #2a2a3e;
                color: #666;
            }
            QPushButton#primaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d9ff, stop:1 #00ff88);
                color: #1a1a2e;
            }
            QPushButton#primaryBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #33e0ff, stop:1 #33ff99);
            }
            QPushButton#dangerBtn {
                background-color: #d63031;
            }
            QPushButton#dangerBtn:hover {
                background-color: #e84343;
            }
            QTextEdit {
                background-color: #0f0f1a;
                border: 1px solid #0f3460;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 12px;
            }
            QLabel {
                color: #e4e4e4;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00d9ff;
            }
            QLabel#subtitleLabel {
                font-size: 13px;
                color: #888;
            }
            QLabel#metricValue {
                font-size: 28px;
                font-weight: bold;
                color: #00ff88;
            }
            QLabel#metricLabel {
                font-size: 11px;
                color: #888;
                text-transform: uppercase;
            }
            QFrame#card {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame#statusIndicator {
                background-color: #666;
                border-radius: 6px;
                min-width: 12px;
                max-width: 12px;
                min-height: 12px;
                max-height: 12px;
            }
            QFrame#statusIndicatorActive {
                background-color: #00ff88;
            }
            QFrame#statusIndicatorWarning {
                background-color: #ffd93d;
            }
        """)

    def create_header(self) -> QWidget:
        """Create the header section."""
        header = QFrame()
        header.setObjectName("card")
        layout = QHBoxLayout(header)

        # Title section
        title_section = QVBoxLayout()
        title = QLabel("Facial Detection & Emotion Analysis")
        title.setObjectName("titleLabel")
        title_section.addWidget(title)

        subtitle = QLabel("Real-time emotion detection with deception analysis")
        subtitle.setObjectName("subtitleLabel")
        title_section.addWidget(subtitle)

        layout.addLayout(title_section)
        layout.addStretch()

        # Hotkeys info
        hotkeys_layout = QVBoxLayout()
        hotkeys_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        hotkey1 = QLabel("Ctrl+Shift+M - Toggle Monitoring")
        hotkey1.setStyleSheet("color: #888; font-size: 11px;")
        hotkeys_layout.addWidget(hotkey1)

        hotkey2 = QLabel("Ctrl+Shift+O - Toggle Overlay")
        hotkey2.setStyleSheet("color: #888; font-size: 11px;")
        hotkeys_layout.addWidget(hotkey2)

        layout.addLayout(hotkeys_layout)

        return header

    def create_status_card(self) -> QFrame:
        """Create the status card."""
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("System Status")
        header_label.setStyleSheet("font-weight: bold; color: #00d9ff; font-size: 14px;")
        header_layout.addWidget(header_label)

        self.status_indicator = QFrame()
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setFixedSize(12, 12)
        header_layout.addWidget(self.status_indicator)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Status text
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.status_label)

        # Status details
        self.status_detail = QLabel("Initialize monitoring to begin")
        self.status_detail.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.status_detail)

        layout.addStretch()
        return card

    def create_metrics_card(self) -> QFrame:
        """Create the metrics card."""
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        # Header
        header_label = QLabel("Live Metrics")
        header_label.setStyleSheet("font-weight: bold; color: #00d9ff; font-size: 14px;")
        layout.addWidget(header_label)

        # Metrics row
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(30)

        # FPS
        fps_section = QVBoxLayout()
        fps_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fps_value = QLabel("0")
        self.fps_value.setObjectName("metricValue")
        fps_section.addWidget(self.fps_value)
        fps_label = QLabel("FPS")
        fps_label.setObjectName("metricLabel")
        fps_section.addWidget(fps_label)
        metrics_row.addLayout(fps_section)

        # Faces
        faces_section = QVBoxLayout()
        faces_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.faces_value = QLabel("0")
        self.faces_value.setObjectName("metricValue")
        faces_section.addWidget(self.faces_value)
        faces_label = QLabel("Faces")
        faces_label.setObjectName("metricLabel")
        faces_section.addWidget(faces_label)
        metrics_row.addLayout(faces_section)

        # Alerts
        alerts_section = QVBoxLayout()
        alerts_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alerts_value = QLabel("0")
        self.alerts_value.setObjectName("metricValue")
        self.alerts_value.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffd93d;")
        alerts_section.addWidget(self.alerts_value)
        alerts_label = QLabel("Alerts")
        alerts_label.setObjectName("metricLabel")
        alerts_section.addWidget(alerts_label)
        metrics_row.addLayout(alerts_section)

        layout.addLayout(metrics_row)
        layout.addStretch()
        return card

    def create_controls(self) -> QFrame:
        """Create the controls section."""
        controls = QFrame()
        controls.setObjectName("card")
        layout = QHBoxLayout(controls)
        layout.setSpacing(12)

        # Start/Stop button
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setObjectName("primaryBtn")
        self.start_button.clicked.connect(self.toggle_monitoring)
        self.start_button.setMinimumHeight(45)
        layout.addWidget(self.start_button)

        # Overlay button
        self.overlay_button = QPushButton("Show Overlay")
        self.overlay_button.clicked.connect(self.toggle_overlay)
        self.overlay_button.setEnabled(False)
        self.overlay_button.setMinimumHeight(45)
        layout.addWidget(self.overlay_button)

        # Mesh toggle button (mesh enabled by default)
        self.mesh_button = QPushButton("Hide Face Mesh")
        self.mesh_button.clicked.connect(self.toggle_mesh)
        self.mesh_button.setEnabled(False)
        self.mesh_button.setMinimumHeight(45)
        layout.addWidget(self.mesh_button)

        # Test page button
        self.test_page_button = QPushButton("Open Test Page")
        self.test_page_button.clicked.connect(self.open_test_page)
        self.test_page_button.setMinimumHeight(45)
        layout.addWidget(self.test_page_button)

        return controls

    def create_log_section(self) -> QFrame:
        """Create the event log section."""
        log_frame = QFrame()
        log_frame.setObjectName("card")
        layout = QVBoxLayout(log_frame)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Event Log")
        header_label.setStyleSheet("font-weight: bold; color: #00d9ff; font-size: 14px;")
        header_layout.addWidget(header_label)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Log text
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        layout.addWidget(self.log_text)

        return log_frame

    def setup_hotkeys(self):
        """Setup keyboard shortcuts."""
        hotkeys_config = self.config.get('ui', {}).get('hotkeys', {})

        # Toggle overlay
        overlay_hotkey = hotkeys_config.get('toggle_overlay', 'Ctrl+Shift+O')
        self.overlay_shortcut = QShortcut(QKeySequence(overlay_hotkey), self)
        self.overlay_shortcut.activated.connect(self.toggle_overlay)

        # Toggle monitoring
        monitoring_hotkey = hotkeys_config.get('toggle_monitoring', 'Ctrl+Shift+M')
        self.monitoring_shortcut = QShortcut(QKeySequence(monitoring_hotkey), self)
        self.monitoring_shortcut.activated.connect(self.toggle_monitoring)

        # Toggle mesh (Ctrl+Shift+F)
        self.mesh_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        self.mesh_shortcut.activated.connect(self.toggle_mesh)

    def initialize_session(self):
        """Initialize the detection session."""
        self.log("Initializing session...")
        self.status_detail.setText("Loading models...")

        self.session_manager = SessionManager(self.config)
        if self.session_manager.initialize():
            self.log("[OK] Session initialized successfully")
            self.overlay = TransparentOverlay(self.config)
            self.status_detail.setText("Ready to start monitoring")
        else:
            self.log("[ERROR] Failed to initialize session")
            self.status_label.setText("Initialization Failed")
            self.status_detail.setText("Check console for errors")
            self.status_indicator.setStyleSheet("background-color: #d63031; border-radius: 6px;")

    def toggle_monitoring(self):
        """Start or stop monitoring."""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """Start face detection and emotion analysis."""
        if not self.session_manager or not self.session_manager.is_initialized:
            self.log("[ERROR] Cannot start - session not initialized")
            return

        self.session_manager.start(frame_callback=None)  # We'll use thread instead
        self.is_monitoring = True

        # Start background processing thread
        self.processing_thread = ProcessingThread(self.session_manager)
        self.processing_thread.frame_processed.connect(self.on_frame_analyzed)
        self.processing_thread.start()

        # Start UI update timer
        self.ui_timer.start(200)  # Update UI 5 times per second

        # Start overlay keep-alive timer to maintain visibility when app loses focus
        if not hasattr(self, 'overlay_timer'):
            self.overlay_timer = QTimer()
            self.overlay_timer.timeout.connect(self._keep_overlay_on_top)
        self.overlay_timer.start(100)  # Check every 100ms

        self.start_button.setText("Stop Monitoring")
        self.start_button.setObjectName("dangerBtn")
        self.start_button.setStyle(self.start_button.style())
        self.overlay_button.setEnabled(True)
        self.mesh_button.setEnabled(True)
        self.status_label.setText("Monitoring Active")
        self.status_detail.setText("Analyzing screen for faces...")
        self.status_indicator.setStyleSheet("background-color: #00ff88; border-radius: 6px;")

        self.log("[OK] Monitoring started")

    def stop_monitoring(self):
        """Stop monitoring."""
        # Stop background thread
        if self.processing_thread:
            self.processing_thread.stop()
            self.processing_thread = None

        self.ui_timer.stop()
        if hasattr(self, 'overlay_timer'):
            self.overlay_timer.stop()
        self.session_manager.stop()
        self.is_monitoring = False

        self.start_button.setText("Start Monitoring")
        self.start_button.setObjectName("primaryBtn")
        self.start_button.setStyle(self.start_button.style())
        self.status_label.setText("Monitoring Stopped")
        self.status_detail.setText("Click Start to resume")
        self.status_indicator.setStyleSheet("background-color: #666; border-radius: 6px;")

        self.log("[OK] Monitoring stopped")

    def update_ui_metrics(self):
        """Update UI metrics display."""
        if self.session_manager and self.session_manager.performance:
            self.fps_value.setText(f"{self.session_manager.performance.current_fps:.0f}")

    def toggle_mesh(self):
        """Toggle facial mesh overlay."""
        if self.overlay:
            is_visible = self.overlay.toggle_mesh()
            if is_visible:
                self.mesh_button.setText("Hide Face Mesh")
                self.log("Facial mesh overlay enabled")
            else:
                self.mesh_button.setText("Show Face Mesh")
                self.log("Facial mesh overlay disabled")

    def _keep_overlay_on_top(self):
        """Keep overlay visible even when main window loses focus."""
        # Disabled - was too aggressive and blocked user interaction
        # The WindowStaysOnTopHint flag should handle this
        pass

    def open_test_page(self):
        """Open the test page in the default browser."""
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        test_page_path = os.path.join(project_root, 'tests', 'emotion_test_page.html')

        # Start HTTP server if not running
        if self.http_server_process is None or self.http_server_process.poll() is not None:
            try:
                self.http_server_process = subprocess.Popen(
                    ['python3', '-m', 'http.server', '8080', '--bind', '127.0.0.1'],
                    cwd=project_root,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.log("[OK] Started local HTTP server on port 8080")
                time.sleep(0.5)  # Give server time to start
            except Exception as e:
                self.log(f"[ERROR] Failed to start HTTP server: {e}")

        # Open test page in browser
        test_url = "http://127.0.0.1:8080/tests/emotion_test_page.html"
        try:
            webbrowser.open(test_url)
            self.log(f"[OK] Opened test page: {test_url}")
        except Exception as e:
            self.log(f"[ERROR] Failed to open browser: {e}")

    def on_frame_analyzed(self, frame_analysis, frame):
        """
        Callback when a frame has been analyzed.

        Args:
            frame_analysis: Frame analysis results
            frame: Original frame image
        """
        if not frame_analysis:
            return

        # Update UI metrics
        self.faces_value.setText(str(len(frame_analysis.faces)))

        # Update overlay if visible (runs on main thread via signal)
        if self.overlay_visible and self.overlay:
            self.overlay.update_analysis(frame_analysis)

        # Log deception events (only log once per face)
        for face in frame_analysis.faces:
            if face.is_deceptive and face.deception_confidence > 0.8:
                # Update alerts counter
                current_alerts = int(self.alerts_value.text())
                self.alerts_value.setText(str(current_alerts + 1))

                self.log(
                    f"[ALERT] DECEPTION DETECTED - Face {face.face_id}: "
                    f"{face.deception_reason} (Confidence: {face.deception_confidence:.0%})"
                )

    def toggle_overlay(self):
        """Toggle overlay visibility."""
        if not self.overlay:
            return

        if self.overlay_visible:
            self.overlay.hide()
            self.overlay_button.setText("Show Overlay")
            self.overlay_visible = False
            self.log("Overlay hidden")
        else:
            self.overlay.show()
            self.overlay_button.setText("Hide Overlay")
            self.overlay_visible = True
            self.log("Overlay shown")

    def log(self, message: str):
        """Add message to event log."""
        # Color code based on message type
        if "[OK]" in message:
            message = f'<span style="color: #00ff88;">{message}</span>'
        elif "[ERROR]" in message:
            message = f'<span style="color: #ff6b6b;">{message}</span>'
        elif "[ALERT]" in message:
            message = f'<span style="color: #ffd93d;">{message}</span>'

        self.log_text.append(message)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.session_manager:
            self.session_manager.shutdown()

        if self.overlay:
            self.overlay.close()

        # Stop HTTP server if running
        if self.http_server_process:
            self.http_server_process.terminate()

        event.accept()
