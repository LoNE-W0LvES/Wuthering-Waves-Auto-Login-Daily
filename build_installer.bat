@echo off
echo ============================================================
echo Wuthering Waves Lunite Auto-Login - Installer Builder
echo ============================================================
echo.

REM Check if Inno Setup is installed
echo Checking for Inno Setup...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo [OK] Found Inno Setup 6
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    echo [OK] Found Inno Setup 6
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo [ERROR] Inno Setup not found!
    echo.
    echo Please download and install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo.
echo Checking required files...

REM Check if built app folder exists
if not exist "WUWATracker_v2.0.0" (
    echo [ERROR] WUWATracker_v2.0.0 folder not found!
    echo Please build the application first using build_exe.py
    echo.
    pause
    exit /b 1
)
echo [OK] WUWATracker_v2.0.0 folder found

REM Check if installer script exists
if not exist "installer.iss" (
    echo [ERROR] installer.iss not found!
    echo.
    pause
    exit /b 1
)
echo [OK] installer.iss found

REM Check if info file exists
if not exist "installer_info.txt" (
    echo [ERROR] installer_info.txt not found!
    echo.
    pause
    exit /b 1
)
echo [OK] installer_info.txt found

REM Check if license exists
if not exist "LICENSE.txt" (
    echo [ERROR] LICENSE.txt not found!
    echo.
    pause
    exit /b 1
)
echo [OK] LICENSE.txt found

echo.
echo ============================================================
echo Building installer...
echo ============================================================
echo.

REM Create output directory
if not exist "installer_output" mkdir installer_output

REM Compile the installer
%ISCC% installer.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Installer built successfully!
    echo ============================================================
    echo.
    echo Output: installer_output\WUWALuniteAutoLogin_Setup_v2.0.0.exe
    echo.
    echo You can now distribute this single installer file!
    echo.
) else (
    echo.
    echo ============================================================
    echo [ERROR] Build failed!
    echo ============================================================
    echo.
    echo Check the error messages above for details.
    echo.
)

pause
