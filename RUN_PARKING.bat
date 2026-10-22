@echo off
cd /d "%~dp0"
echo Starting ParkPilot Smart Mall Parking...
echo Make sure Arduino Serial Monitor is closed.
echo Website: http://127.0.0.1:5000
python app.py
pause
