# ============================================================
# File: game_controller.py
# ============================================================
import os
import psutil
import subprocess
from datetime import datetime

# Import our modules
try:
    from config import debug_print
    from screen_detector import ScreenDetector, WIN32_AVAILABLE
except ImportError as e:
    debug_print(f"✗ Import error: {e}")
    WIN32_AVAILABLE = False


    # Fallback debug print
    def debug_print(msg, data=None):
        print(msg)
        if data:
            print(data)

# Import win32 modules if available
if WIN32_AVAILABLE:
    try:
        import win32gui
        import win32con
        import win32api
    except ImportError:
        WIN32_AVAILABLE = False
        debug_print("✗ win32 modules not available")


class GameController:
    """Handles game launching and window interaction"""

    def __init__(self, config):
        self.config = config
        self.screen_detector = ScreenDetector()
        debug_print("GameController initialized")

    def is_game_running(self):
        """Check if the game process is currently running"""
        process_name = self.config.get("game_process_name", "Client-Win64-Shipping.exe")

        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            debug_print(f"✗ Error checking if game is running: {e}")

        return False

    def launch_game(self, game_path):
        """Launch the game executable"""
        if not game_path or not os.path.exists(game_path):
            debug_print(f"✗ Game path invalid: {game_path}")
            return False

        try:
            debug_print(f"Launching game: {game_path}")
            subprocess.Popen([game_path])
            debug_print("✓ Game launch command sent")
            return True
        except Exception as e:
            debug_print(f"✗ Error launching game: {e}")
            return False

    def click_login_screen(self):
        """
        Detect and click login screen using visual detection
        3-step process:
        1. Check for "Login Status: 0"
        2. Check for "Tap to land in Solaris-3" text
        3. Wait 5 seconds, focus window, move mouse, and click

        Returns: "clicked", "waiting_login_status", "waiting_tap_text", "not_found", or "error"
        """
        try:
            # Find game window
            window_info = self.screen_detector.find_game_window()
            if not window_info:
                debug_print("✗ Game window not found")
                return "not_found"

            # Capture screenshot
            screenshot = self.screen_detector.capture_window(window_info)
            if not screenshot:
                debug_print("✗ Failed to capture screenshot")
                return "error"

            # Save debug screenshot
            saved_path = self.screen_detector.save_debug_screenshot(screenshot)

            # Step 1: Check for "Login Status: 0"
            login_status_ready, login_text = self.screen_detector.detect_login_ready(screenshot)

            if not login_status_ready:
                return "waiting_login_status"

            # Step 2: Check for "Tap to land in Solaris-3" text
            tap_text_ready, tap_text = self.screen_detector.detect_tap_to_land_text(screenshot)

            if not tap_text_ready:
                return "waiting_tap_text"

            # Both indicators found! Now get click position
            click_x, click_y = self.screen_detector.get_click_position(screenshot)

            if click_x is None or click_y is None:
                debug_print("✗ Could not calculate click position")
                return "error"

            debug_print("✓ All indicators found! Starting click sequence...")

            # Step 3: Wait 5 seconds before clicking
            import time
            debug_print("⏳ Waiting 5 seconds before clicking...")
            time.sleep(5)

            if WIN32_AVAILABLE:
                hwnd = window_info["hwnd"]

                # Bring window to foreground and focus it
                try:
                    debug_print("Focusing game window...")
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.5)
                    debug_print("✓ Window focused")
                except Exception as e:
                    debug_print(f"⚠ Could not bring window to foreground: {e}")

                # Move mouse to the position
                try:
                    rect = window_info["rect"]
                    abs_x = rect[0] + click_x
                    abs_y = rect[1] + click_y

                    debug_print(f"Moving mouse to ({abs_x}, {abs_y})...")
                    win32api.SetCursorPos((abs_x, abs_y))
                    time.sleep(0.3)
                    debug_print("✓ Mouse positioned")
                except Exception as e:
                    debug_print(f"⚠ Could not move mouse: {e}")

                # Send click to the window
                try:
                    debug_print(f"Sending click at relative position ({click_x}, {click_y})...")
                    lParam = win32api.MAKELONG(click_x, click_y)

                    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
                    time.sleep(0.1)
                    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

                    debug_print("✓ Click sent successfully!")
                    return "clicked"
                except Exception as e:
                    debug_print(f"✗ Error sending click: {e}")
                    return "error"
            else:
                debug_print("✗ Cannot click - win32 not available")
                return "error"

        except Exception as e:
            debug_print(f"✗ Error in click_login_screen: {e}")
            import traceback
            debug_print(traceback.format_exc())
            return "error"

    def check_for_patcher(self):
        """
        Check for Notice/Patcher window and handle it intelligently
        Returns:
        - "update_complete" - Update/patch finished, clicked Exit
        - "network_error" - Network error detected
        - "patching" - Still patching/updating
        - None - No notice window found
        """
        if not WIN32_AVAILABLE:
            return None

        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        windows.append((hwnd, title))
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            for hwnd, title in windows:
                # Look for Notice window
                if "Notice" in title or "notice" in title.lower():
                    debug_print(f"Found Notice window: '{title}'")

                    # Try to get all text from the window
                    window_text = ""

                    def collect_text(hwnd_child, texts):
                        text = win32gui.GetWindowText(hwnd_child)
                        if text and len(text.strip()) > 0:
                            texts.append(text.strip())
                        return True

                    texts = []
                    try:
                        win32gui.EnumChildWindows(hwnd, collect_text, texts)
                        window_text = " ".join(texts).lower()
                        debug_print(f"Notice window text: '{window_text[:100]}'")
                    except Exception as e:
                        debug_print(f"Could not get window text: {e}")

                    # Analyze the text to determine the type of notice
                    notice_type = None

                    if "update complete" in window_text or "patch" in window_text and "complete" in window_text:
                        notice_type = "update_complete"
                        debug_print("✓ Detected: Update/Patch Complete")
                    elif "patching complete" in window_text or "restart the game" in window_text:
                        notice_type = "update_complete"
                        debug_print("✓ Detected: Patching Complete - Restart Required")
                    elif "network" in window_text and ("error" in window_text or "fail" in window_text):
                        notice_type = "network_error"
                        debug_print("⚠ Detected: Network Error")
                    elif "update" in window_text or "patch" in window_text or "download" in window_text:
                        notice_type = "patching"
                        debug_print("⏳ Detected: Updating/Patching in progress")
                    else:
                        notice_type = "unknown"
                        debug_print(f"⚠ Unknown notice type")

                    # Look for Exit button
                    def find_exit_button(hwnd_child, buttons):
                        text = win32gui.GetWindowText(hwnd_child)
                        class_name = win32gui.GetClassName(hwnd_child)
                        if text and "exit" in text.lower() and "button" in class_name.lower():
                            buttons.append((hwnd_child, text))
                            debug_print(f"Found button: '{text}' ({class_name})")
                        return True

                    buttons = []
                    win32gui.EnumChildWindows(hwnd, find_exit_button, buttons)

                    # Handle based on notice type
                    if notice_type == "update_complete":
                        debug_print("Update complete - will click Exit after 2 seconds")
                        import time
                        time.sleep(2)

                        if buttons:
                            win32gui.PostMessage(buttons[0][0], win32con.WM_LBUTTONDOWN, 0, 0)
                            win32gui.PostMessage(buttons[0][0], win32con.WM_LBUTTONUP, 0, 0)
                            debug_print("✓ Exit button clicked")
                            return "update_complete"
                        else:
                            debug_print("⚠ Exit button not found, trying to close window")
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            return "update_complete"

                    elif notice_type == "network_error":
                        debug_print("Network error - will click Exit after 2 seconds")
                        import time
                        time.sleep(2)

                        if buttons:
                            win32gui.PostMessage(buttons[0][0], win32con.WM_LBUTTONDOWN, 0, 0)
                            win32gui.PostMessage(buttons[0][0], win32con.WM_LBUTTONUP, 0, 0)
                            debug_print("✓ Exit button clicked")
                            return "network_error"
                        else:
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            return "network_error"

                    elif notice_type == "patching":
                        debug_print("Patching in progress - waiting...")
                        return "patching"

                    else:
                        # Unknown type, but there's a notice window
                        debug_print("Unknown notice type - treating as update complete")
                        if buttons:
                            import time
                            time.sleep(2)
                            win32gui.PostMessage(buttons[0][0], win32con.WM_LBUTTONDOWN, 0, 0)
                            win32gui.PostMessage(buttons[0][0], win32con.WM_LBUTTONUP, 0, 0)
                            return "update_complete"

        except Exception as e:
            debug_print(f"✗ Error checking patcher: {e}")
            import traceback
            debug_print(traceback.format_exc())

        return None