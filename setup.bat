@echo off
title Strategic Dashboard - Setup

echo ============================================
echo   Strategic Dashboard - Initial Setup
echo ============================================
echo.

REM --- Python check ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM --- pip install ---
echo Installing dependencies...
pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup complete!
echo   Double-click START.vbs to launch.
echo ============================================
pause
