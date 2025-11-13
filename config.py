# ============================================================
# File: config.py
# ============================================================
import json
import os
from datetime import datetime
from pprint import pprint

# Global debug flag
DEBUG = True


def debug_print(message, data=None):
    """Print debug messages when DEBUG is True"""
    if DEBUG:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
        if data is not None:
            pprint(data, indent=2)


class Config:
    """Configuration manager"""

    def __init__(self, config_file="ww_launcher_config.json"):
        self.config_file = config_file
        self.default_config = {
            "game_path": "",
            "game_process_name": "Client-Win64-Shipping.exe",
            "auto_launch_time": "23:50",
            "reset_time": "02:00",
            "required_playtime_minutes": 30,
            "fallback_retry_minutes": 10,
            "login_wait_min_seconds": 15,
            "login_wait_max_seconds": 90,
            "screenshot_check_interval": 2,
            "system_enabled": True  # NEW: Enable/disable entire system
        }
        self.data = self.load()

    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                debug_print("✓ Config loaded from file")
                return config
            except Exception as e:
                debug_print(f"✗ Error loading config: {e}")
                return self.default_config.copy()
        else:
            debug_print("Using default config (file not found)")
            return self.default_config.copy()

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            debug_print("✓ Config saved")
        except Exception as e:
            debug_print(f"✗ Error saving config: {e}")

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        """Get value with default fallback"""
        return self.data.get(key, default)


class Tracking:
    """Tracking data manager with optimized saving"""

    def __init__(self, tracking_file="ww_launcher_tracking.json"):
        self.tracking_file = tracking_file
        self.default_tracking = {
            "current_reset_period": None,
            "game_started": False,
            "start_time": None,
            "start_method": None,
            "total_playtime_seconds": 0,
            "requirement_met": False,
            "auto_launch_attempted": False,
            "last_process_check": None,
            "patcher_exit_clicked": False,
            "patcher_exit_time": None,
            "waiting_after_patch": False,
            "game_closed_early": False,
            "early_close_time": None,
            "fallback_retry_count": 0,
            "login_clicked": False,
            "login_click_time": None,
            "last_screenshot_check": None
        }
        self.data = self.load()

        # NEW: Track last save time for throttling
        self.last_save_time = None
        self.save_interval_seconds = 60  # Save at most once per minute
        self.pending_save = False

    def load(self):
        """Load tracking data from file"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    tracking = json.load(f)
                # Merge with defaults
                for key, value in self.default_tracking.items():
                    if key not in tracking:
                        tracking[key] = value
                debug_print("✓ Tracking loaded from file")
                return tracking
            except Exception as e:
                debug_print(f"✗ Error loading tracking: {e}")
                return self.default_tracking.copy()
        else:
            debug_print("Using default tracking (file not found)")
            return self.default_tracking.copy()

    def save(self, force=False):
        """
        Save tracking data to file (throttled)
        Only saves once per minute unless force=True
        """
        now = datetime.now()

        # Check if we should save
        should_save = force
        if not should_save and self.last_save_time:
            elapsed = (now - self.last_save_time).total_seconds()
            should_save = elapsed >= self.save_interval_seconds
        elif not should_save and not self.last_save_time:
            should_save = True  # First save

        if should_save:
            try:
                with open(self.tracking_file, 'w') as f:
                    json.dump(self.data, f, indent=4)
                self.last_save_time = now
                self.pending_save = False
                debug_print("✓ Tracking saved")
            except Exception as e:
                debug_print(f"✗ Error saving tracking: {e}")
        else:
            # Mark that we have pending changes
            self.pending_save = True

    def force_save(self):
        """Force immediate save (for important events)"""
        self.save(force=True)

    def reset(self, current_period):
        """Reset tracking for new period"""
        debug_print(f"Resetting tracking for period: {current_period}")
        self.data = self.default_tracking.copy()
        self.data["current_reset_period"] = current_period
        self.force_save()

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        """Get value with default fallback"""
        return self.data.get(key, default)