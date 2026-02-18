@echo off
title Strategic Dashboard

REM --- Move to script directory ---
cd /d "%~dp0"

REM --- Check if already running ---
netstat -ano | findstr ":8502" >nul 2>&1
if not errorlevel 1 (
    echo Dashboard is already running on port 8502.
    echo Opening browser...
    start http://localhost:8502
    exit /b 0
)

echo ============================================
echo   Strategic Dashboard - Starting...
echo ============================================
echo.

REM --- Open browser after short delay ---
start /b cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:8502"

REM --- Launch Streamlit ---
python -m streamlit run app_new.py --server.port 8502 --server.headless true
