@echo off
cd /d "%~dp0"
title ParkPilot - Public Website Server (COM13)
echo ==============================================
echo Smart Mall Parking - Public Website Server
echo ==============================================
echo Close Arduino Serial Monitor and other parking servers first.
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: Could not install packages. Check your Python installation.
  pause
  exit /b 1
)
echo.
echo Starting the website on port 5000...
python public_server.py
pause
