# 🌊 Wuthering Waves Lunite Auto-Login

**Never miss your daily Lunite subscription rewards again!**

An automated tool that logs into Wuthering Waves daily to collect your Lunite subscription Astrite rewards before the daily reset. Perfect for busy players who sometimes forget to login.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📋 Table of Contents

- [Features](#-features)
- [Why This Tool?](#-why-this-tool)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Building Executable](#-building-executable)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Features
- 🎯 **Automatic Daily Login** - Launches game at your specified time
- 🖱️ **OCR-Based Login Detection** - Automatically detects and clicks the login screen
- ⏱️ **Playtime Tracking** - Ensures you stay logged in long enough
- 🔄 **Daily Reset Handling** - Resets tracking at 2:00 AM (configurable)
- 🎮 **Game Process Monitoring** - Tracks if game is running
- 🔧 **Patcher/Update Handling** - Automatically handles game updates

### Smart Features
- 🤖 **Intelligent Login Detection** - Uses visual OCR to detect "Login Status: 0" and "Tap to land in Solaris-3" text
- 🔁 **Retry Logic** - Handles network errors and retries automatically
- 📊 **System Tray Integration** - Runs quietly in the background
- 🚀 **Windows Startup** - Optional: Launch automatically with Windows
- ⏸️ **Enable/Disable System** - Toggle automation on/off without closing the app
- 💾 **Persistent Tracking** - Remembers your daily progress even if you restart the app

### User-Friendly
- 🎨 **Clean, Modern UI** - Easy to understand interface
- 📝 **Real-time Status Updates** - See what's happening at the bottom of the window
- 🔔 **Tray Notifications** - Get notified of important events
- 🛠️ **Manual Controls** - Launch/close game manually for testing

---

## 🎮 Why This Tool?

If you have a **Lunite subscription** (monthly card) in Wuthering Waves, you need to **login every day** to collect your daily Astrite rewards. Miss a day, and you lose those rewards forever!

This tool ensures you **never miss a day** by:
1. Automatically launching the game before daily reset
2. Detecting the login screen using OCR
3. Clicking to login automatically
4. Staying logged in for the required time
5. Tracking your daily progress

Perfect for:
- 💼 Busy professionals who might forget to login
- 🌍 Travelers in different time zones
- 😴 Players who don't want to wake up for daily reset
- 🎯 Anyone who wants to maximize their Lunite subscription value

---

## 🔧 How It Works

### The Process

1. **Scheduled Launch** (e.g., 11:50 PM)
   - App waits until your configured auto-launch time
   - Launches Wuthering Waves executable

2. **Update Handling**
   - Detects if game needs to update/patch
   - Automatically clicks "Exit" when update completes
   - Relaunches the game

3. **Login Detection** (15-90 seconds after launch)
   - Takes screenshots of the game window
   - Uses OCR to detect "Login Status: 0" text
   - Detects "Tap to land in Solaris-3" text
   - Waits 5 seconds, then clicks the login area

4. **Playtime Tracking**
   - Monitors game process
   - Tracks how long you've been logged in
   - Confirms daily requirement is met (default: 30 minutes)

5. **Daily Reset** (2:00 AM by default)
   - Resets all tracking for the new day
   - Ready for next daily login

### Visual Detection

The tool uses **OCR (Optical Character Recognition)** to actually read text from the game screen:

- **"Login Status: 0"** → Indicates the login screen is ready
- **"Tap to land in Solaris-3"** → Confirms you're on the landing screen
- **Smart Click Position** → Clicks in a safe area to avoid buttons

---

## 📦 Installation

### Prerequisites

- **Windows 10/11** (64-bit)
- **Python 3.8+** (if running from source)
- **Wuthering Waves** installed

### Option 1: Download Compiled Executable (Easiest)

1. Go to [Releases](https://github.com/yourusername/wuwa-lunite-autologin/releases)
2. Download the latest `WUWATracker_vX.X.X.zip`
3. Extract the ZIP file
4. Run `WUWATracker.exe`

⚠️ **Important**: Keep all files together! The `tesseract_bundle` folder is required for OCR.

### Option 2: Run From Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/wuwa-lunite-autologin.git
   cd wuwa-lunite-autologin
   ```

2. **Install Python dependencies**
   ```bash
   pip install PySide6 psutil opencv-python pillow numpy pywin32 pytesseract
   ```

3. **Download Tesseract OCR**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location OR create a `tesseract_bundle` folder with:
     - `tesseract.exe`
     - `tessdata/` folder with language files

4. **Run the application**
   ```bash
   python main.py
   ```

---

## 🚀 Usage

### First Time Setup

1. **Launch the application**
   - Run `WUWATracker.exe` or `python main.py`

2. **Configure game path**
   - Click "Browse" next to "Game Executable"
   - Navigate to your game installation (usually: `D:\Games\Wuthering Waves\Wuthering Waves Game\Wuthering Waves.exe`)

3. **Set auto-launch time**
   - Set to a time **before** daily reset (e.g., 11:50 PM if reset is at 2:00 AM)
   - This gives enough time for updates and login

4. **Configure playtime**
   - Default: 30 minutes (recommended)
   - This ensures you stay logged in long enough

5. **Click "Save Settings"**

6. **Optional: Enable Windows Startup**
   - Check "Add to Windows Startup"
   - App will launch automatically when Windows starts

### Daily Operation

1. **Minimize to tray** (click minimize button)
   - App runs in the background
   - Shows status in system tray icon

2. **The app will automatically:**
   - Launch the game at your specified time
   - Handle updates/patches
   - Detect and click the login screen
   - Track your playtime
   - Reset at 2:00 AM for the next day

3. **Check status anytime:**
   - Double-click tray icon to show window
   - Or right-click for quick status menu

### Manual Controls

- **🚀 Launch Game Now** - Test game launch manually
- **❌ Close Game** - Force close the game process
- **🔄 Reset Daily Status** - Reset tracking for testing

---

## ⚙️ Configuration

### Settings Explained

| Setting | Description | Default | Notes |
|---------|-------------|---------|-------|
| **Game Executable** | Path to Wuthering Waves.exe | - | Must be set before first use |
| **Game Process Name** | Process name to monitor | `Client-Win64-Shipping.exe` | Usually don't need to change |
| **Required Playtime** | Minutes to stay logged in | 30 | Increase if you want longer sessions |
| **Screenshot Check Interval** | How often to check for login screen (seconds) | 2 | Lower = more frequent checks |
| **Auto-Launch Time** | When to launch game daily | 23:50 | Set before your daily reset |
| **Daily Reset Time** | When tracking resets | 02:00 | Match your server's reset time |

### Advanced Settings (in config file)

Edit `ww_launcher_config.json` for advanced options:

```json
{
  "login_wait_min_seconds": 15,    // Wait at least 15s before checking login
  "login_wait_max_seconds": 90,    // Stop checking after 90s
  "system_enabled": true           // Enable/disable automation
}
```

---

## 🔨 Building Executable

Want to build your own executable?

### Prerequisites

```bash
pip install nuitka
```

### Build Steps

1. **Prepare tesseract_bundle**
   - Create `tesseract_bundle` folder
   - Add `tesseract.exe` and `tessdata/` folder

2. **Add icon (optional)**
   - Place `icon.ico` in the project folder
   - Will be embedded in the executable

3. **Run build script**
   ```bash
   python build_exe.py
   ```

4. **Wait for compilation** (5-15 minutes first time)

5. **Find your executable**
   - Look in `WUWATracker_vX.X.X/` folder
   - Contains everything needed to run

### Build Configuration

The build script (`build_exe.py`):
- Creates standalone executable (no Python required)
- Embeds icon if `icon.ico` exists
- Requests admin privileges (for game launching)
- Includes all dependencies
- Creates README with instructions

---

## 🔍 Troubleshooting

### Common Issues

#### ❌ "OCR not available"
**Problem**: Tesseract OCR is not configured

**Solutions**:
- Make sure `tesseract_bundle` folder exists next to the executable
- Check that `tesseract_bundle/tesseract.exe` exists
- Verify `tesseract_bundle/tessdata/eng.traineddata` exists

#### ❌ "Game window not found"
**Problem**: Can't detect the game window

**Solutions**:
- Make sure the game is actually running
- Check that window title contains "Wuthering" or "Kuro"
- Don't minimize the game during detection

#### ❌ Login detection not working
**Problem**: Not clicking the login screen

**Solutions**:
- Wait 15-90 seconds after launch for detection to start
- Make sure game is in windowed or borderless mode (not fullscreen)
- Check `debug_screenshot.png` to see what OCR detected
- Try adjusting "Screenshot Check Interval" to 1 second

#### ❌ Game won't launch
**Problem**: Auto-launch fails

**Solutions**:
- Verify game path is correct (click Browse and select again)
- Run the app as Administrator
- Check if antivirus is blocking the launcher
- Try "Launch Game Now" button to test manually

#### ❌ App won't start
**Problem**: Executable won't open

**Solutions**:
- Make sure all files from ZIP are extracted together
- Don't move the .exe away from other files
- Check Windows Event Viewer for error details
- Try running from command prompt to see errors

### Debug Mode

Enable detailed logging by editing `config.py`:

```python
DEBUG = True  # Already enabled by default
```

Check console output for detailed information about what's happening.

---

## ❓ FAQ

### General Questions

**Q: Is this safe to use?**  
A: Yes! This tool only interacts with the game at the OS level (launching it and clicking). It doesn't modify game files or memory. However, use at your own risk.

**Q: Will I get banned?**  
A: This tool doesn't modify the game or use any injection/hooking. It just launches the game and clicks the screen like a human would. However, automation is a gray area - use at your own discretion.

**Q: Does it collect my login credentials?**  
A: No! The tool never touches your login information. It only clicks the game screen after you're already logged in.

**Q: Can I use this without Lunite subscription?**  
A: Yes, but it's designed for Lunite subscribers who need daily logins. You can use it just to auto-launch the game if you want.

### Technical Questions

**Q: Why does it need admin privileges?**  
A: Some games require admin rights to launch properly. The tool requests admin to ensure it can launch the game.

**Q: How much CPU/RAM does it use?**  
A: Very minimal - around 50-100MB RAM and negligible CPU when idle. Spikes briefly during OCR checks.

**Q: Can I run multiple instances?**  
A: Not recommended. One instance per game installation is enough.

**Q: Does it work with other games?**  
A: It's specifically designed for Wuthering Waves login detection. The OCR looks for game-specific text.

### Configuration Questions

**Q: What time should I set for auto-launch?**  
A: Set it 1-2 hours before daily reset. For example, if reset is at 2:00 AM, set to 11:50 PM or 12:00 AM. This gives time for updates.

**Q: How long should "Required Playtime" be?**  
A: 30 minutes is safe. You can reduce to 5-10 minutes if you just want to collect rewards quickly.

**Q: Can I change the reset time?**  
A: Yes! Edit "Daily Reset Time" to match your server's reset time.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

1. Check [existing issues](https://github.com/yourusername/wuwa-lunite-autologin/issues)
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Screenshots if applicable
   - Your Windows version and Python version

### Suggesting Features

Open an issue with the `enhancement` label and describe:
- What feature you'd like
- Why it would be useful
- How it should work

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/wuwa-lunite-autologin.git
cd wuwa-lunite-autologin

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Run the app
python main.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 LoNE WoLvES

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **Kuro Games** - For creating Wuthering Waves
- **Tesseract OCR** - For the excellent OCR engine
- **PySide6** - For the GUI framework
- **Community** - For feedback and testing

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/wuwa-lunite-autologin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/wuwa-lunite-autologin/discussions)

---

## ⚠️ Disclaimer

This tool is provided as-is for educational and convenience purposes. The developers are not responsible for any consequences of using this tool, including but not limited to account bans or data loss. Use at your own risk.

This is an unofficial tool and is not affiliated with, endorsed by, or associated with Kuro Games or Wuthering Waves.

---

## 🌟 Star History

If you find this tool helpful, please consider giving it a star! ⭐

---

**Made with ❤️ for the Wuthering Waves community**

[⬆ Back to Top](#-wuthering-waves-lunite-auto-login)


