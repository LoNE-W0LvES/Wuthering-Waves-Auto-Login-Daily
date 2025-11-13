"""
Nuitka Build Script for WUWA Tracker
Simple build - just copy tesseract_bundle folder next to the exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configuration
APP_NAME = "WUWATracker"
VERSION = "2.0.0"
COMPANY_NAME = "LoNE WoLvES"
COPYRIGHT = "Copyright (c) 2025 LoNE WoLvES. All rights reserved."


def check_prerequisites():
    """Check if all required tools are installed"""
    print("=" * 60)
    print("Checking prerequisites...")
    print("=" * 60)

    # Check Nuitka
    try:
        result = subprocess.run([sys.executable, "-m", "nuitka", "--version"],
                              capture_output=True, text=True)
        print(f"✓ Nuitka installed: {result.stdout.strip()}")
    except:
        print("✗ Nuitka not found!")
        print("  Install with: pip install nuitka")
        return False

    # Check if tesseract_bundle exists
    if not os.path.exists("tesseract_bundle"):
        print("✗ tesseract_bundle folder not found!")
        print("  Make sure you have the tesseract_bundle folder in the same directory")
        return False
    else:
        tesseract_exe = os.path.join("tesseract_bundle", "tesseract.exe")
        if os.path.exists(tesseract_exe):
            print(f"✓ tesseract_bundle found with tesseract.exe")
        else:
            print("✗ tesseract.exe not found in tesseract_bundle")
            return False

    # Check required Python packages
    required_packages = [
        "PySide6",
        "psutil",
        "cv2",
        "PIL",
        "numpy",
        "win32gui",
        "pytesseract"
    ]

    missing_packages = []
    for package in required_packages:
        package_import = package
        if package == "cv2":
            package_import = "opencv-python"
        elif package == "PIL":
            package_import = "pillow"
        elif package == "win32gui":
            package_import = "pywin32"

        try:
            if package == "cv2":
                import cv2
            elif package == "PIL":
                import PIL
            elif package == "win32gui":
                import win32gui
            else:
                __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not installed")
            missing_packages.append(package_import)

    if missing_packages:
        print("\nMissing packages. Install with:")
        print(f"  pip install {' '.join(set(missing_packages))}")
        return False

    print("\n✓ All prerequisites satisfied!\n")
    return True


def build_executable():
    """Build the executable with Nuitka"""
    print("=" * 60)
    print("Building executable with Nuitka...")
    print("=" * 60)
    print("This may take 5-15 minutes on first build...")
    print()

    # Build Nuitka command - standalone mode (creates a folder)
    nuitka_cmd = [
        sys.executable,
        "-m", "nuitka",
        "--standalone",
        "--windows-console-mode=disable",
        "--enable-plugin=pyside6",
        f"--company-name={COMPANY_NAME}",
        f"--product-name=WUWA Tracker",
        f"--file-version={VERSION}.0",
        f"--product-version={VERSION}",
        f"--file-description=Wuthering Waves Daily Tracker with Auto Login",
        f"--copyright={COPYRIGHT}",
        f"--output-dir=build",
        "main.py"
    ]

    # Add icon if it exists
    if os.path.exists("icon.ico"):
        nuitka_cmd.insert(-1, "--windows-icon-from-ico=icon.ico")
        print("✓ Using icon.ico for executable icon")

    # Add manifest for admin privileges
    if os.path.exists("app.manifest"):
        nuitka_cmd.insert(-1, "--windows-uac-admin")
        print("✓ Using app.manifest - will request admin privileges")

    print()

    # Run Nuitka
    try:
        result = subprocess.run(nuitka_cmd, check=True)
        print("\n" + "=" * 60)
        print("✓ Build completed successfully!")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print(f"Error code: {e.returncode}")
        return False


def create_distribution():
    """Create the final distribution folder"""
    print("\n" + "=" * 60)
    print("Creating distribution folder...")
    print("=" * 60)

    build_folder = Path("build/main.dist")
    if not build_folder.exists():
        print("✗ Build folder not found")
        return False

    # Create distribution folder
    dist_folder = Path(f"{APP_NAME}_v{VERSION}")
    if dist_folder.exists():
        shutil.rmtree(dist_folder)

    print(f"Copying build to {dist_folder}...")
    shutil.copytree(build_folder, dist_folder)

    # Rename main.exe to our app name
    old_exe = dist_folder / "main.exe"
    new_exe = dist_folder / f"{APP_NAME}.exe"
    if old_exe.exists():
        shutil.move(str(old_exe), str(new_exe))
        print(f"✓ Renamed to {APP_NAME}.exe")

    # Copy tesseract_bundle to the distribution folder
    print("Copying tesseract_bundle...")
    tesseract_src = Path("tesseract_bundle")
    tesseract_dst = dist_folder / "tesseract_bundle"
    shutil.copytree(tesseract_src, tesseract_dst)
    print("✓ tesseract_bundle copied")

    # Create README
    readme_content = f"""WUWA Tracker v{VERSION}
{COPYRIGHT}

IMPORTANT: This folder contains everything needed to run the tracker.
Keep all files together!

REQUIREMENTS:
- Windows 10/11
- Wuthering Waves game installed

HOW TO USE:
1. Run {APP_NAME}.exe
2. Click "Browse" to select your game executable
   (Usually: Wuthering Waves Game/Wuthering Waves.exe)
3. Set your desired auto-launch time
4. Set required playtime (default: 30 minutes)
5. Click "Save Settings"
6. Minimize to system tray - the tracker will run in the background

FEATURES:
✓ Automatic game launch at specified time
✓ OCR-based login detection (auto-clicks login screen)
✓ Playtime tracking
✓ Daily reset at 2:00 AM (configurable)
✓ System tray support
✓ Manual controls for testing

FOLDER STRUCTURE:
- {APP_NAME}.exe       (Main tracker)
- tesseract_bundle/    (OCR engine - required!)
- Other DLLs and files (Python runtime - required!)

TROUBLESHOOTING:
- If the tracker doesn't open: Make sure all files are extracted together
- If OCR doesn't work: Verify tesseract_bundle folder is present
- For errors: Run from command prompt to see error messages

For support, contact LoNE WoLvES
"""

    with open(dist_folder / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✓ README.txt created")
    print(f"\n✓ Distribution ready: {dist_folder}/")

    # Show folder structure
    print("\nFolder contents:")
    print(f"  • {APP_NAME}.exe (Main executable)")
    print(f"  • tesseract_bundle/ (OCR engine)")
    print(f"  • README.txt (Instructions)")
    print(f"  • Various DLLs and Python runtime files")

    return True


def cleanup():
    """Clean up build artifacts"""
    print("\n" + "=" * 60)
    print("Cleanup options...")
    print("=" * 60)

    response = input("Remove build folder? (keeps distribution folder) [Y/n]: ")
    if response.lower() != 'n':
        if os.path.exists("build"):
            shutil.rmtree("build")
            print("✓ Removed build folder")
    else:
        print("✓ Kept build folder")


def main():
    """Main build process"""
    print("\n" + "=" * 60)
    print("WUWA Tracker - Build Script")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Company: {COMPANY_NAME}")
    print("=" * 60 + "\n")

    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites check failed!")
        print("Please install missing requirements and try again.")
        input("\nPress Enter to exit...")
        return 1

    # Step 2: Build executable
    if not build_executable():
        print("\nBuild failed. Check the error messages above.")
        input("\nPress Enter to exit...")
        return 1

    # Step 3: Create distribution
    if not create_distribution():
        print("\nDistribution creation failed.")
        input("\nPress Enter to exit...")
        return 1

    # Step 4: Cleanup
    cleanup()

    print("\n" + "=" * 60)
    print("✓ BUILD COMPLETE!")
    print("=" * 60)
    print(f"\n📦 Distribution folder: {APP_NAME}_v{VERSION}/")
    print("\n✓ Ready to distribute!")
    print("\nTo share with others:")
    print(f"  1. Zip the '{APP_NAME}_v{VERSION}' folder")
    print("  2. Send the zip file")
    print("  3. Recipients extract and run the .exe")
    print("\n⚠ Important: Users must extract ALL files together!")
    print("   The tracker needs the tesseract_bundle folder to work.")

    input("\nPress Enter to exit...")
    return 0


if __name__ == "__main__":
    sys.exit(main())