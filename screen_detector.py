# ============================================================
# File: screen_detector.py
# ============================================================
import sys
import os
from pathlib import Path

import numpy as np
from datetime import datetime
from PIL import Image, ImageGrab
import cv2

# Try to import pytesseract for OCR
try:
    import pytesseract

    # Determine base path (works for both script and exe)
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Look for tesseract_bundle in the same folder as the script/exe
    tesseract_path = os.path.join(base_path, 'tesseract_bundle', 'tesseract.exe')
    tessdata_path = os.path.join(base_path, 'tesseract_bundle', 'tessdata')

    # Set both tesseract executable and tessdata path
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Set TESSDATA_PREFIX environment variable
    # IMPORTANT: This should point to the tessdata folder itself, not its parent
    os.environ['TESSDATA_PREFIX'] = os.path.join(base_path, 'tesseract_bundle', 'tessdata')

    # Verify tesseract is accessible
    if os.path.exists(pytesseract.pytesseract.tesseract_cmd):
        OCR_AVAILABLE = True
        print("=" * 60)
        print("✓ TESSERACT OCR FOUND AND CONFIGURED!")
        print("=" * 60)
        print(f"  Base path: {base_path}")
        print(f"  Tesseract exe: {tesseract_path}")
        print(f"  Tessdata folder: {tessdata_path}")
        print(f"  Tessdata exists: {os.path.exists(tessdata_path)}")
        if os.path.exists(tessdata_path):
            traineddata_files = list(Path(tessdata_path).glob("*.traineddata"))
            print(f"  Language files: {len(traineddata_files)} found")
            if any("eng" in f.name for f in traineddata_files):
                print(f"  ✓ English (eng.traineddata) available")
            else:
                print(f"  ⚠ English (eng.traineddata) NOT found!")
        print("=" * 60)
    else:
        OCR_AVAILABLE = False
        print("=" * 60)
        print("✗ TESSERACT OCR NOT FOUND!")
        print("=" * 60)
        print(f"  Looking in: {tesseract_path}")
        print(f"  Base path: {base_path}")
        print(f"  Tessdata folder: {tessdata_path}")
        print(f"  File exists: {os.path.exists(tesseract_path)}")
        print(f"  Folder exists: {os.path.exists(os.path.dirname(tesseract_path))}")
        print("=" * 60)
        print("⚠ Make sure tesseract_bundle folder is next to the exe/script")
        print("=" * 60)

except ImportError:
    OCR_AVAILABLE = False
    print("⚠ pytesseract not available - install with: pip install pytesseract")
except Exception as e:
    OCR_AVAILABLE = False
    print(f"⚠ Error configuring pytesseract: {e}")
    import traceback
    traceback.print_exc()

# Import debug print from config
try:
    from config import debug_print
except ImportError:
    def debug_print(msg, data=None):
        print(msg)
        if data:
            print(data)

# Try to import win32 modules
try:
    import win32gui
    import win32ui
    import win32con
    import win32api

    WIN32_AVAILABLE = True
    debug_print("✓ win32 modules loaded")
except ImportError:
    WIN32_AVAILABLE = False
    debug_print("✗ win32 modules not available - some features disabled")


class ScreenDetector:
    """Detects game elements by actually capturing and analyzing the screen"""

    def __init__(self):
        self.last_screenshot = None
        self.last_screenshot_time = None
        debug_print("ScreenDetector initialized")

    def find_game_window(self):
        """Find the game window and return its handle and dimensions"""
        if not WIN32_AVAILABLE:
            debug_print("✗ Cannot find window - win32gui not available")
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

            debug_print(f"Scanning {len(windows)} visible windows...")

            # Look for game window
            for hwnd, title in windows:
                title_lower = title.lower()
                # Check for Wuthering Waves related keywords
                keywords = ["wuthering", "kuro", "client", "鸣潮", "waves"]

                if any(keyword in title_lower for keyword in keywords):
                    try:
                        rect = win32gui.GetWindowRect(hwnd)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]

                        # Check if window is reasonably sized (not minimized)
                        if width > 800 and height > 600:
                            debug_print(f"✓ Found game window: '{title}'", {
                                "hwnd": hwnd,
                                "width": width,
                                "height": height,
                                "position": (rect[0], rect[1])
                            })
                            return {
                                "hwnd": hwnd,
                                "title": title,
                                "rect": rect,
                                "width": width,
                                "height": height
                            }
                    except Exception as e:
                        debug_print(f"✗ Error checking window '{title}': {e}")
                        continue

            debug_print("✗ Game window not found")
            return None

        except Exception as e:
            debug_print(f"✗ Error finding game window: {e}")
            return None

    def capture_window(self, window_info):
        """Capture screenshot of the game window"""
        if not window_info:
            debug_print("✗ Cannot capture - no window info")
            return None

        try:
            hwnd = window_info["hwnd"]
            rect = window_info["rect"]

            # Get window position
            left, top, right, bottom = rect

            # Capture the screen area
            try:
                screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))

                self.last_screenshot = screenshot
                self.last_screenshot_time = datetime.now()

                debug_print(f"✓ Screenshot captured: {screenshot.size[0]}x{screenshot.size[1]}")
                return screenshot
            except Exception as e:
                debug_print(f"✗ ImageGrab failed: {e}")
                return None

        except Exception as e:
            debug_print(f"✗ Error capturing window: {e}")
            return None

    def detect_login_ready(self, screenshot):
        """
        Step 1: Check if "Login Status: 0" is visible (key indicator)
        Uses OCR to actually read the text
        Returns: (detected: bool, text_found: str)
        """
        if screenshot is None:
            return False, ""

        try:
            img_np = np.array(screenshot)
            height, width = img_np.shape[:2]

            # Extract bottom-right region where "Login Status: 0" appears
            bottom_right_region = img_np[int(height * 0.9):height, int(width * 0.75):width]

            if OCR_AVAILABLE:
                # Use OCR to read text
                try:
                    pil_region = Image.fromarray(bottom_right_region)
                    text = pytesseract.image_to_string(pil_region, config='--psm 6')
                    text_clean = text.strip()

                    debug_print("OCR: Bottom-right region text", text_clean[:50] if text_clean else "")
                except Exception as ocr_error:
                    debug_print(f"✗ OCR failed: {ocr_error}")
                    return False, f"OCR Error: {ocr_error}"

                # Check if "login status" and "0" are present
                text_lower = text_clean.lower()
                if "login" in text_lower and "status" in text_lower and "0" in text_lower:
                    debug_print("✓ 'Login Status: 0' detected!")
                    return True, text_clean

                return False, text_clean
            else:
                # Fallback: pixel-based detection (less reliable)
                gray = cv2.cvtColor(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
                bottom_right_gray = gray[int(height * 0.9):height, int(width * 0.75):width]

                _, text_thresh = cv2.threshold(bottom_right_gray, 150, 255, cv2.THRESH_BINARY)
                text_pixels = np.sum(text_thresh == 255)
                text_density = text_pixels / (bottom_right_gray.shape[0] * bottom_right_gray.shape[1])

                if text_density > 0.02:
                    debug_print("✓ Text detected in bottom-right")
                    return True, f"[No OCR - density: {text_density:.3f}]"

                return False, f"[No OCR - density: {text_density:.3f}]"

        except Exception as e:
            debug_print(f"✗ Error checking login status: {e}")
            return False, ""

    def detect_tap_to_land_text(self, screenshot):
        """
        Step 2: Check if "Tap to land in Solaris-3" text is visible
        Uses OCR to actually read the text
        Returns: (detected: bool, text_found: str)
        """
        if screenshot is None:
            return False, ""

        try:
            img_np = np.array(screenshot)
            height, width = img_np.shape[:2]

            # Focus on lower center where the text appears
            lower_center_y = int(height * 0.65)
            center_x_start = int(width * 0.25)
            center_x_end = int(width * 0.75)

            roi = img_np[lower_center_y:height, center_x_start:center_x_end]

            if OCR_AVAILABLE:
                # Use OCR to read text
                try:
                    pil_region = Image.fromarray(roi)
                    text = pytesseract.image_to_string(pil_region, config='--psm 6')
                    text_clean = text.strip()

                    debug_print("OCR: Center-bottom text", text_clean[:50] if text_clean else "")
                except Exception as ocr_error:
                    debug_print(f"✗ OCR failed: {ocr_error}")
                    return False, f"OCR Error: {ocr_error}"

                # Check if "tap" and "land" and "solaris" are present
                text_lower = text_clean.lower()
                if "tap" in text_lower and "land" in text_lower and "solaris" in text_lower:
                    debug_print("✓ 'Tap to land in Solaris-3' detected!")
                    return True, text_clean

                return False, text_clean
            else:
                # Fallback: pixel-based detection (less reliable)
                gray = cv2.cvtColor(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
                roi_gray = gray[lower_center_y:height, center_x_start:center_x_end]

                _, thresh = cv2.threshold(roi_gray, 180, 255, cv2.THRESH_BINARY)
                text_pixels = np.sum(thresh == 255)
                text_density = text_pixels / (roi_gray.shape[0] * roi_gray.shape[1])

                if text_density > 0.03:
                    debug_print("✓ Text detected in center")
                    return True, f"[No OCR - density: {text_density:.3f}]"

                return False, f"[No OCR - density: {text_density:.3f}]"

        except Exception as e:
            debug_print(f"✗ Error checking tap to land text: {e}")
            return False, ""

    def get_click_position(self, screenshot):
        """
        Step 3: Get a safe position to click (empty area, avoiding buttons)
        Returns: (x, y) coordinates
        """
        if screenshot is None:
            return None, None

        try:
            width, height = screenshot.size

            # Click in upper-left empty area to avoid buttons
            click_x = int(width * 0.35)
            click_y = int(height * 0.45)

            debug_print(f"Click position: ({click_x}, {click_y})")
            return click_x, click_y

        except Exception as e:
            debug_print(f"✗ Error calculating click position: {e}")
            return None, None

    def save_debug_screenshot(self, screenshot, filename="debug_screenshot.png"):
        """Save screenshot for debugging"""
        try:
            if screenshot:
                abs_path = os.path.abspath(filename)
                screenshot.save(abs_path)
                debug_print(f"✓ Debug screenshot saved: {abs_path}")
                return abs_path
            else:
                debug_print("✗ No screenshot to save")
                return None
        except Exception as e:
            debug_print(f"✗ Error saving debug screenshot: {e}")
            return None