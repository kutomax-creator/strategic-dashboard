@echo off
title Strategic Dashboard - Stop

echo Stopping Strategic Dashboard...

REM --- Kill Streamlit processes ---
taskkill /f /im streamlit.exe >nul 2>&1

REM --- Kill Python processes on port 8502 ---
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8502" ^| findstr "LISTENING"') do (
    echo Killing PID %%a ...
    taskkill /f /pid %%a >nul 2>&1
)

echo Dashboard stopped.
timeout /t 2 /nobreak >nul
