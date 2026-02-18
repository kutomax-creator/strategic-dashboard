@echo off
title Strategic Dashboard - Build EXE

echo ============================================
echo   Building Strategic Dashboard .exe
echo ============================================
echo.
echo Run this on a Windows PC where pip works.
echo.

REM --- Move to script directory ---
cd /d "%~dp0"

REM --- Install dependencies ---
echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed
    pause
    exit /b 1
)

echo.
echo [2/3] Building .exe with PyInstaller...
echo (This may take several minutes)
echo.

pyinstaller --noconfirm --clean ^
    --name "StrategicDashboard" ^
    --icon=NUL ^
    --windowed ^
    --add-data "app_new.py;." ^
    --add-data "opening.png;." ^
    --add-data "back.png;." ^
    --add-data "assets;assets" ^
    --add-data "dashboard_modules;dashboard_modules" ^
    --add-data "context;context" ^
    --add-data "static;static" ^
    --hidden-import=streamlit ^
    --hidden-import=streamlit.runtime.scriptrunner ^
    --hidden-import=streamlit.web.cli ^
    --hidden-import=anthropic ^
    --hidden-import=yfinance ^
    --hidden-import=feedparser ^
    --hidden-import=PIL ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=pypdf ^
    --collect-all streamlit ^
    --collect-all streamlit_ext ^
    main_desktop.py

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [3/3] Finalizing...
if not exist "dist\StrategicDashboard\context" mkdir "dist\StrategicDashboard\context"
if not exist "dist\StrategicDashboard\static" mkdir "dist\StrategicDashboard\static"

echo.
echo ============================================
echo   Build complete!
echo   Output: dist\StrategicDashboard\
echo ============================================
echo.
echo Copy dist\StrategicDashboard\ to the target PC.
echo Double-click StrategicDashboard.exe to launch.
echo.
pause
