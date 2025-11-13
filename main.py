import sys
import os
import psutil
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QLineEdit,
                               QTimeEdit, QFileDialog, QGroupBox, QMessageBox,
                               QSystemTrayIcon, QMenu, QCheckBox)
from PySide6.QtCore import QTimer, QTime, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction

# Import our modules
from config import Config, Tracking, debug_print, DEBUG
from game_controller import GameController


class WutheringWavesLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        debug_print("=== Initializing Wuthering Waves Launcher ===")

        # Initialize config and tracking
        self.config = Config()
        self.tracking = Tracking()
        self.game_controller = GameController(self.config.data)

        # Check and reset period if needed
        self.check_and_reset_period()

        # Initialize UI
        self.init_ui()

        # Log Tesseract status
        self.log_tesseract_status()

        self.create_tray_icon()
        self.start_timer()

    def log_tesseract_status(self):
        """Log Tesseract OCR status"""
        try:
            from screen_detector import OCR_AVAILABLE
            import pytesseract

            if OCR_AVAILABLE:
                status_msg = "✓ OCR Enabled"
            else:
                status_msg = "✗ OCR Disabled - Login detection may not work"

            self.update_status_message(status_msg)

        except Exception as e:
            self.update_status_message(f"Error checking OCR: {e}")

    def update_status_message(self, message):
        """Update the status message at the bottom of the window"""
        if hasattr(self, 'status_message_label'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.status_message_label.setText(f"[{timestamp}] {message}")

    def check_and_reset_period(self):
        """Check if we're in a new reset period and reset tracking if needed"""
        current_period = self.get_current_reset_period_id()

        if self.tracking["current_reset_period"] != current_period:
            debug_print(f"New reset period: {current_period}")
            self.tracking.reset(current_period)

    def get_current_reset_period_id(self):
        """Get unique identifier for current reset period"""
        reset_start = self.get_current_reset_start()
        return reset_start.strftime("%Y-%m-%d")

    def get_current_reset_start(self):
        """Get the start time of current reset period"""
        now = datetime.now()
        reset_hour, reset_minute = map(int, self.config["reset_time"].split(':'))
        today_reset = now.replace(hour=reset_hour, minute=reset_minute, second=0, microsecond=0)

        if now >= today_reset:
            return today_reset
        else:
            return today_reset - timedelta(days=1)

    def get_next_reset_time(self):
        """Get the next reset time"""
        now = datetime.now()
        reset_hour, reset_minute = map(int, self.config["reset_time"].split(':'))
        next_reset = now.replace(hour=reset_hour, minute=reset_minute, second=0, microsecond=0)

        if now >= next_reset:
            next_reset += timedelta(days=1)

        return next_reset

    def update_playtime(self):
        """Update playtime if game is running"""
        if self.game_controller.is_game_running():
            if not self.tracking["game_started"]:
                debug_print("Game process detected - marking as started")
                self.tracking["game_started"] = True
                self.tracking["start_time"] = datetime.now().isoformat()
                if not self.tracking["start_method"]:
                    self.tracking["start_method"] = "external"

                self.tracking["game_closed_early"] = False
                self.tracking["early_close_time"] = None
                self.tracking.force_save()

            if self.tracking["start_time"]:
                start_dt = datetime.fromisoformat(self.tracking["start_time"])
                elapsed = (datetime.now() - start_dt).total_seconds()
                self.tracking["total_playtime_seconds"] = int(elapsed)

                required_seconds = self.config["required_playtime_minutes"] * 60
                if self.tracking["total_playtime_seconds"] >= required_seconds:
                    if not self.tracking["requirement_met"]:
                        debug_print("✓ Daily requirement MET!")
                        self.tracking["requirement_met"] = True
                        self.tracking.force_save()

                self.tracking["last_process_check"] = datetime.now().isoformat()
                self.tracking.save()
        else:
            if self.tracking["game_started"] and self.tracking["start_time"]:
                debug_print("Game process stopped")

                start_dt = datetime.fromisoformat(self.tracking["start_time"])
                final_playtime = int((datetime.now() - start_dt).total_seconds())
                self.tracking["total_playtime_seconds"] = final_playtime
                debug_print(f"Final playtime recorded: {final_playtime}s ({final_playtime // 60}m)")

                self.tracking["start_time"] = None

                required_seconds = self.config["required_playtime_minutes"] * 60
                if not self.tracking["requirement_met"] and self.tracking["total_playtime_seconds"] < required_seconds:
                    if not self.tracking["game_closed_early"]:
                        debug_print("⚠ Game closed early without meeting requirement")
                        self.tracking["game_closed_early"] = True
                        self.tracking["early_close_time"] = datetime.now().isoformat()

                self.tracking["last_process_check"] = datetime.now().isoformat()
                self.tracking.force_save()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Wuthering Waves Daily Launcher v2.0")
        self.setFixedSize(650, 580)  # Fixed size - not resizable
        self.setWindowIcon(self.create_app_icon())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Status Group
        status_group = QGroupBox("Daily Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.status_label.setFont(font)
        status_layout.addWidget(self.status_label)

        self.playtime_label = QLabel()
        self.playtime_label.setAlignment(Qt.AlignCenter)
        playtime_font = QFont()
        playtime_font.setPointSize(10)
        self.playtime_label.setFont(playtime_font)
        status_layout.addWidget(self.playtime_label)

        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_font = QFont()
        timer_font.setPointSize(14)
        self.timer_label.setFont(timer_font)
        status_layout.addWidget(self.timer_label)

        self.game_status_label = QLabel()
        self.game_status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.game_status_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Settings Group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()

        # System Enable/Disable
        self.system_enabled_checkbox = QCheckBox("Enable Auto-Launch System")
        self.system_enabled_checkbox.setChecked(self.config.get("system_enabled", True))
        self.system_enabled_checkbox.setStyleSheet("font-weight: bold;")
        self.system_enabled_checkbox.stateChanged.connect(self.on_system_enabled_changed)
        settings_layout.addWidget(self.system_enabled_checkbox)

        # Add to Startup
        self.startup_checkbox = QCheckBox("Add to Windows Startup")
        self.startup_checkbox.setChecked(self.is_in_startup())
        self.startup_checkbox.stateChanged.connect(self.on_startup_changed)
        settings_layout.addWidget(self.startup_checkbox)

        settings_layout.addSpacing(10)

        # Game Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Game Executable:"))
        self.path_input = QLineEdit(self.config["game_path"] or "")
        path_layout.addWidget(self.path_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_game_path)
        path_layout.addWidget(browse_btn)
        settings_layout.addLayout(path_layout)

        # Process Name
        process_layout = QHBoxLayout()
        process_layout.addWidget(QLabel("Game Process Name:"))
        self.process_input = QLineEdit(self.config["game_process_name"] or "Client-Win64-Shipping.exe")
        process_layout.addWidget(self.process_input)
        settings_layout.addLayout(process_layout)

        # Required Playtime
        playtime_layout = QHBoxLayout()
        playtime_layout.addWidget(QLabel("Required Playtime (minutes):"))
        self.playtime_input = QLineEdit(str(self.config["required_playtime_minutes"] or 30))
        self.playtime_input.setMaximumWidth(100)
        playtime_layout.addWidget(self.playtime_input)
        playtime_layout.addStretch()
        settings_layout.addLayout(playtime_layout)

        # Screenshot Check Interval
        screenshot_layout = QHBoxLayout()
        screenshot_layout.addWidget(QLabel("Screenshot Check Interval (seconds):"))
        screenshot_interval = self.config["screenshot_check_interval"] or 2
        self.screenshot_input = QLineEdit(str(screenshot_interval))
        self.screenshot_input.setMaximumWidth(100)
        screenshot_layout.addWidget(self.screenshot_input)
        screenshot_layout.addWidget(QLabel("(How often to check for login screen)"))
        screenshot_layout.addStretch()
        settings_layout.addLayout(screenshot_layout)

        # Auto Launch Time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Auto-Launch Time:"))
        self.time_edit = QTimeEdit()
        hour, minute = map(int, self.config["auto_launch_time"].split(':'))
        self.time_edit.setTime(QTime(hour, minute))
        time_layout.addWidget(self.time_edit)
        settings_layout.addLayout(time_layout)

        # Reset Time
        reset_time_layout = QHBoxLayout()
        reset_time_layout.addWidget(QLabel("Daily Reset Time:"))
        self.reset_time_edit = QTimeEdit()
        reset_hour, reset_minute = map(int, self.config["reset_time"].split(':'))
        self.reset_time_edit.setTime(QTime(reset_hour, reset_minute))
        reset_time_layout.addWidget(self.reset_time_edit)
        settings_layout.addLayout(reset_time_layout)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Manual Controls
        controls_group = QGroupBox("Manual Controls")
        controls_layout = QHBoxLayout()

        launch_btn = QPushButton("🚀 Launch Game Now")
        launch_btn.clicked.connect(self.launch_game_manually)
        controls_layout.addWidget(launch_btn)

        close_game_btn = QPushButton("❌ Close Game")
        close_game_btn.clicked.connect(self.close_game_manually)
        controls_layout.addWidget(close_game_btn)

        reset_status_btn = QPushButton("🔄 Reset Daily Status")
        reset_status_btn.clicked.connect(self.reset_daily_status)
        controls_layout.addWidget(reset_status_btn)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Status Message (replaces debug console)
        self.status_message_label = QLabel()
        self.status_message_label.setStyleSheet(
            "background-color: #f0f0f0; color: #333; padding: 8px; "
            "border: 1px solid #ccc; border-radius: 3px; font-family: monospace;"
        )
        self.status_message_label.setWordWrap(True)
        self.status_message_label.setText("[00:00:00] Ready")
        layout.addWidget(self.status_message_label)

        # Copyright Notice
        copyright_label = QLabel("© 2025 LoNE WoLvES - All Rights Reserved")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #666; font-size: 9px; padding: 5px;")
        layout.addWidget(copyright_label)

    def is_in_startup(self):
        """Check if app is in Windows startup folder"""
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'),
                                          r'Microsoft\Windows\Start Menu\Programs\Startup')
            shortcut_path = os.path.join(startup_folder, 'WutheringWavesLauncher.lnk')
            return os.path.exists(shortcut_path)
        except Exception as e:
            debug_print(f"Error checking startup: {e}")
            return False

    def on_startup_changed(self, state):
        """Handle startup checkbox change"""
        enabled = state == Qt.Checked

        try:
            startup_folder = os.path.join(os.getenv('APPDATA'),
                                          r'Microsoft\Windows\Start Menu\Programs\Startup')
            shortcut_path = os.path.join(startup_folder, 'WutheringWavesLauncher.lnk')

            if enabled:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)

                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(sys.argv[0])

                shortcut.TargetPath = exe_path
                shortcut.WorkingDirectory = os.path.dirname(exe_path)
                shortcut.IconLocation = exe_path
                shortcut.save()

                self.update_status_message("✓ Added to Windows Startup")
                QMessageBox.information(self, "Success", "Added to Windows Startup!")
            else:
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
                    self.update_status_message("✓ Removed from Windows Startup")
                    QMessageBox.information(self, "Success", "Removed from Windows Startup!")

        except Exception as e:
            self.update_status_message(f"✗ Startup error: {e}")
            QMessageBox.warning(self, "Error", f"Failed to modify startup:\n{e}")
            self.startup_checkbox.setChecked(self.is_in_startup())

    def on_system_enabled_changed(self, state):
        """Handle system enabled/disabled state change"""
        enabled = state == Qt.Checked
        self.config["system_enabled"] = enabled
        self.config.save()

        if enabled:
            self.update_status_message("✓ System ENABLED - Auto-launch will work")
        else:
            self.update_status_message("⚠ System DISABLED - No auto-launch or automated actions")

        self.update_status_display()

    def create_app_icon(self):
        """Create app icon from icon.ico file or fallback to generated icon"""
        # Try to load icon.ico from file
        if os.path.exists("icon.ico"):
            try:
                icon = QIcon("icon.ico")
                if not icon.isNull():
                    return icon
            except Exception as e:
                debug_print(f"Could not load icon.ico: {e}")

        # Fallback: Create a simple app icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        from PySide6.QtGui import QPainter, QColor
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(70, 130, 180))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        painter.end()

        return QIcon(pixmap)

    def create_tray_icon(self):
        """Create system tray icon with menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_app_icon())

        tray_menu = QMenu()

        self.show_action = QAction("Show Window", self)
        self.show_action.triggered.connect(self.show_window)
        tray_menu.addAction(self.show_action)

        self.hide_action = QAction("Hide to Tray", self)
        self.hide_action.triggered.connect(self.hide_to_tray)
        tray_menu.addAction(self.hide_action)

        tray_menu.addSeparator()

        self.tray_toggle_action = QAction("Disable System", self)
        self.tray_toggle_action.triggered.connect(self.toggle_system_from_tray)
        tray_menu.addAction(self.tray_toggle_action)

        tray_menu.addSeparator()

        launch_action = QAction("Launch Game Now", self)
        launch_action.triggered.connect(self.launch_game_manually)
        tray_menu.addAction(launch_action)

        close_game_action = QAction("Close Game", self)
        close_game_action.triggered.connect(self.close_game_manually)
        tray_menu.addAction(close_game_action)

        tray_menu.addSeparator()

        self.tray_status_action = QAction("Status: Loading...", self)
        self.tray_status_action.setEnabled(False)
        tray_menu.addAction(self.tray_status_action)

        self.tray_playtime_action = QAction("Playtime: 0m", self)
        self.tray_playtime_action.setEnabled(False)
        tray_menu.addAction(self.tray_playtime_action)

        tray_menu.addSeparator()

        exit_action = QAction("Exit Application", self)
        exit_action.triggered.connect(self.exit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        self.update_tray_tooltip()
        self.update_status_display()

    def toggle_system_from_tray(self):
        """Toggle system enabled state from tray menu"""
        current_state = self.config.get("system_enabled", True)
        new_state = not current_state

        self.config["system_enabled"] = new_state
        self.config.save()
        self.system_enabled_checkbox.setChecked(new_state)

        if new_state:
            self.tray_icon.showMessage("System Enabled", "Auto-launch is now active", QSystemTrayIcon.Information, 2000)
        else:
            self.tray_icon.showMessage("System Disabled", "Auto-launch is now inactive", QSystemTrayIcon.Warning, 2000)

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def show_window(self):
        """Show the main window"""
        self.show()
        self.activateWindow()
        self.raise_()

    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        self.tray_icon.showMessage(
            "WW Launcher",
            "Minimized to tray - Right-click tray icon for menu",
            QSystemTrayIcon.Information,
            2000
        )

    def changeEvent(self, event):
        """Handle window state changes (minimize, etc)"""
        if event.type() == event.Type.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                # When minimized, hide to tray
                event.ignore()
                self.hide_to_tray()
        super().changeEvent(event)

    def closeEvent(self, event):
        """Override close event - X button closes the app"""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Do you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Save any pending changes
            if self.tracking.pending_save:
                self.tracking.force_save()
            self.tray_icon.hide()
            event.accept()
            QApplication.quit()
        else:
            event.ignore()

    def exit_application(self):
        """Exit the application"""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Exit application?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            debug_print("=== Application exiting ===")
            if self.tracking.pending_save:
                self.tracking.force_save()
            self.tray_icon.hide()
            QApplication.quit()

    def update_tray_tooltip(self):
        """Update tray tooltip"""
        if not hasattr(self, 'tray_icon'):
            return

        system_enabled = self.config.get("system_enabled", True)

        if not system_enabled:
            status = "⏸ DISABLED"
        elif self.tracking["requirement_met"]:
            status = "✓ Complete"
        elif self.game_controller.is_game_running():
            status = "⏱ Playing"
        elif self.tracking["game_started"]:
            status = "⏸ Closed"
        else:
            status = "⚠ Pending"

        minutes = self.tracking["total_playtime_seconds"] // 60
        tooltip = f"WW Launcher - {status}\nPlaytime: {minutes}m"
        self.tray_icon.setToolTip(tooltip)

        if hasattr(self, 'tray_status_action'):
            self.tray_status_action.setText(f"Status: {status}")
            self.tray_playtime_action.setText(f"Playtime: {minutes}m/{self.config['required_playtime_minutes']}m")

        if hasattr(self, 'tray_toggle_action'):
            if system_enabled:
                self.tray_toggle_action.setText("Disable System")
            else:
                self.tray_toggle_action.setText("Enable System")

    def browse_game_path(self):
        """Browse for game executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Game Executable",
            "",
            "Executable Files (*.exe);;All Files (*.*)"
        )
        if file_path:
            self.path_input.setText(file_path)
            self.update_status_message(f"Game path selected: {file_path}")

    def save_settings(self):
        """Save settings"""
        self.config["game_path"] = self.path_input.text()
        self.config["game_process_name"] = self.process_input.text()
        self.config["auto_launch_time"] = self.time_edit.time().toString("HH:mm")
        self.config["reset_time"] = self.reset_time_edit.time().toString("HH:mm")

        try:
            self.config["required_playtime_minutes"] = int(self.playtime_input.text())
            self.config["screenshot_check_interval"] = int(self.screenshot_input.text())
        except:
            QMessageBox.warning(self, "Error", "Invalid numbers!")
            return

        self.config.save()
        self.update_status_message("Settings saved successfully")
        QMessageBox.information(self, "Saved", "Settings saved!")
        self.update_status_display()

    def launch_game_manually(self):
        """Manual game launch"""
        self.update_status_message("Manual launch requested")
        if self.launch_game("manual"):
            self.tracking["start_method"] = "manual"
            self.tracking.force_save()

    def close_game_manually(self):
        """Close the game process"""
        process_name = self.config.get("game_process_name", "Client-Win64-Shipping.exe")

        try:
            killed = False
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        self.update_status_message(f"Terminated game process (PID: {proc.info['pid']})")
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            if killed:
                QMessageBox.information(self, "Success", "Game process terminated!")
            else:
                QMessageBox.information(self, "Info", "Game is not running")

        except Exception as e:
            self.update_status_message(f"✗ Error closing game: {e}")
            QMessageBox.critical(self, "Error", f"Failed to close game:\n{e}")

    def launch_game(self, method="automatic"):
        """Launch the game"""
        game_path = self.config["game_path"]

        if not game_path or not os.path.exists(game_path):
            self.update_status_message(f"ERROR: Game not found: {game_path}")
            QMessageBox.warning(self, "Error", "Game executable not found!")
            return False

        self.update_status_message(f"Launching game ({method})...")
        if self.game_controller.launch_game(game_path):
            self.tracking["game_started"] = True
            self.tracking["start_time"] = datetime.now().isoformat()
            self.tracking["start_method"] = method
            self.tracking["game_closed_early"] = False
            self.tracking["login_clicked"] = False

            if method == "automatic":
                self.tracking["auto_launch_attempted"] = True

            self.tracking.force_save()
            self.update_status_display()
            self.update_status_message("✓ Game launched successfully")

            if method == "manual":
                QMessageBox.information(self, "Launched", "Game launched!")

            return True
        else:
            self.update_status_message("✗ Launch failed")
            return False

    def reset_daily_status(self):
        """Reset daily status"""
        reply = QMessageBox.question(
            self,
            "Reset",
            "Reset today's progress?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.update_status_message("Resetting daily status...")
            self.tracking.reset(self.get_current_reset_period_id())
            self.update_status_display()
            QMessageBox.information(self, "Reset", "Status reset!")

    def start_timer(self):
        """Start update timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.update_status_message("Timer started - System ready")

    def update_timer(self):
        """Main update loop"""
        system_enabled = self.config.get("system_enabled", True)

        if not system_enabled:
            self.update_playtime()
            self.update_status_display()
            return

        self.check_and_reset_period()

        patcher_status = self.game_controller.check_for_patcher()

        if patcher_status == "update_complete":
            self.update_status_message("✓ Update/Patch complete - Exit clicked")
            self.tracking["patcher_exit_clicked"] = True
            self.tracking["patcher_exit_time"] = datetime.now().isoformat()
            self.tracking["patcher_type"] = "update"
            self.tracking["waiting_after_patch"] = True
            self.tracking.force_save()

        elif patcher_status == "network_error":
            self.update_status_message("⚠ Network error detected - Exit clicked")
            self.tracking["patcher_exit_clicked"] = True
            self.tracking["patcher_exit_time"] = datetime.now().isoformat()
            self.tracking["patcher_type"] = "network"
            self.tracking["waiting_after_patch"] = True
            self.tracking.force_save()

        elif patcher_status == "patching":
            self.update_status_message("⏳ Game is patching/updating...")

        if self.tracking.get("waiting_after_patch") and self.tracking.get("patcher_exit_time"):
            exit_time = datetime.fromisoformat(self.tracking["patcher_exit_time"])
            time_since_exit = (datetime.now() - exit_time).total_seconds()

            patcher_type = self.tracking.get("patcher_type", "update")

            if patcher_type == "update":
                wait_time = 10
                if time_since_exit >= wait_time:
                    self.update_status_message("Relaunching after update (10s wait)...")
                    self.tracking["waiting_after_patch"] = False
                    self.tracking["patcher_exit_clicked"] = False
                    self.tracking.save()

                    if not self.game_controller.is_game_running():
                        self.launch_game("automatic_after_patch")

            elif patcher_type == "network":
                wait_time = 600
                if time_since_exit >= wait_time:
                    self.update_status_message("Relaunching after network error (10min wait)...")
                    self.tracking["waiting_after_patch"] = False
                    self.tracking["patcher_exit_clicked"] = False
                    self.tracking.save()

                    if not self.game_controller.is_game_running():
                        self.launch_game("automatic_after_network_error")

        if (self.tracking["game_started"] and
                not self.tracking["login_clicked"] and
                self.tracking["start_time"]):

            start_dt = datetime.fromisoformat(self.tracking["start_time"])
            time_since_start = (datetime.now() - start_dt).total_seconds()

            min_wait = self.config["login_wait_min_seconds"] or 15
            max_wait = self.config["login_wait_max_seconds"] or 90

            if min_wait <= time_since_start <= max_wait:
                last_check = self.tracking["last_screenshot_check"]
                check_interval = self.config["screenshot_check_interval"] or 2

                should_check = True
                if last_check:
                    last_check_dt = datetime.fromisoformat(last_check)
                    should_check = (datetime.now() - last_check_dt).total_seconds() >= check_interval

                if should_check:
                    self.tracking["last_screenshot_check"] = datetime.now().isoformat()
                    self.tracking.save()

                    result = self.game_controller.click_login_screen()

                    if result == "clicked":
                        self.update_status_message("✓ Login clicked!")
                        self.tracking["login_clicked"] = True
                        self.tracking["login_click_time"] = datetime.now().isoformat()
                        self.tracking.force_save()
                    elif result == "waiting_login_status":
                        self.update_status_message("⏳ Waiting for 'Login Status: 0'...")
                    elif result == "waiting_tap_text":
                        self.update_status_message("⏳ Waiting for 'Tap to land' text...")
                    elif result == "not_found":
                        self.update_status_message("⚠ Game window not found")

        self.update_playtime()

        now = datetime.now()
        if not self.tracking["requirement_met"] and not self.tracking["auto_launch_attempted"]:
            auto_launch_time_str = self.config["auto_launch_time"]
            hour, minute = map(int, auto_launch_time_str.split(':'))
            auto_launch_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if now >= auto_launch_time:
                next_reset = self.get_next_reset_time()
                if now < next_reset and not self.game_controller.is_game_running():
                    self.update_status_message("Auto-launch time reached!")
                    self.launch_game("automatic")

        self.update_status_display(patcher_status)

    def update_status_display(self, patcher_status=None):
        """Update UI status"""
        system_enabled = self.config.get("system_enabled", True)

        waiting_after_patch = False
        wait_time_remaining = 0
        wait_reason = ""

        if self.tracking.get("waiting_after_patch") and self.tracking.get("patcher_exit_time"):
            exit_time = datetime.fromisoformat(self.tracking["patcher_exit_time"])
            time_since_exit = (datetime.now() - exit_time).total_seconds()
            patcher_type = self.tracking.get("patcher_type", "update")

            if patcher_type == "update":
                total_wait = 10
                if time_since_exit < total_wait:
                    waiting_after_patch = True
                    wait_time_remaining = int(total_wait - time_since_exit)
                    wait_reason = "update/patch"
            elif patcher_type == "network":
                total_wait = 600
                if time_since_exit < total_wait:
                    waiting_after_patch = True
                    wait_time_remaining = int(total_wait - time_since_exit)
                    wait_reason = "network error"

        if not system_enabled:
            self.status_label.setText("⏸ System DISABLED")
            self.status_label.setStyleSheet("color: red;")
        elif waiting_after_patch:
            minutes = wait_time_remaining // 60
            seconds = wait_time_remaining % 60
            self.status_label.setText(f"⏳ Waiting to relaunch ({minutes}m {seconds}s)")
            self.status_label.setStyleSheet("color: orange;")
        elif self.tracking["requirement_met"]:
            self.status_label.setText("✓ Daily requirement completed!")
            self.status_label.setStyleSheet("color: green;")
        elif self.game_controller.is_game_running():
            self.status_label.setText("⏱ Playing now...")
            self.status_label.setStyleSheet("color: blue;")
        elif self.tracking["game_started"]:
            self.status_label.setText("⏸ Game closed (played today)")
            self.status_label.setStyleSheet("color: gray;")
        else:
            self.status_label.setText("⚠ Not started today")
            self.status_label.setStyleSheet("color: orange;")

        minutes = self.tracking["total_playtime_seconds"] // 60
        seconds = self.tracking["total_playtime_seconds"] % 60
        required = self.config["required_playtime_minutes"] or 30

        playtime_text = f"Playtime: {minutes}m {seconds}s / {required}m"
        if self.tracking["start_method"]:
            playtime_text += f" ({self.tracking['start_method']})"
        self.playtime_label.setText(playtime_text)

        if not system_enabled:
            self.game_status_label.setText("⏸ Automation disabled")
            self.game_status_label.setStyleSheet("color: red;")
        elif waiting_after_patch:
            self.game_status_label.setText(f"⏳ Will relaunch after {wait_reason} ({wait_time_remaining}s)")
            self.game_status_label.setStyleSheet("color: orange;")
        elif patcher_status == "patching":
            self.game_status_label.setText("⏳ Game is updating/patching...")
            self.game_status_label.setStyleSheet("color: orange;")
        elif self.game_controller.is_game_running():
            self.game_status_label.setText("🎮 Game running")
            self.game_status_label.setStyleSheet("color: green;")
        else:
            self.game_status_label.setText("Game not running")
            self.game_status_label.setStyleSheet("color: gray;")

        next_reset = self.get_next_reset_time()
        time_until = next_reset - datetime.now()
        self.timer_label.setText(f"Next reset: {self.format_timedelta(time_until)}")

        self.update_tray_tooltip()

    def format_timedelta(self, td):
        """Format timedelta"""
        total_seconds = int(td.total_seconds())
        if total_seconds < 0:
            return "00:00:00"
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    print("=== Wuthering Waves Launcher v2.0 ===")
    print("Visual Detection with OCR Enabled")
    print(f"Debug Mode: {DEBUG}")
    print("\nRequired dependencies:")
    print("  pip install PySide6 psutil opencv-python pillow numpy pywin32 pytesseract")
    print("\nFor OCR to work, also install Tesseract-OCR:")
    print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("\nFor startup functionality, also install:")
    print("  pip install pywin32")
    print()

    window = WutheringWavesLauncher()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()