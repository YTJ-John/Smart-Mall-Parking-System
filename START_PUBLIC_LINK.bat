@echo off
cd /d "%~dp0"
title ParkPilot - Public HTTPS Link
where cloudflared >nul 2>&1
if errorlevel 1 (
  echo Cloudflare Tunnel is not installed or not in PATH.
  echo Install via Windows Terminal using:
  echo winget install -e --id Cloudflare.cloudflared
  echo Then close this window and start it again.
  pause
  exit /b 1
)
echo Generating a temporary public HTTPS address...
echo Your website must already be running in START_PUBLIC_WEBSITE.bat
cloudflared tunnel --url http://127.0.0.1:5000
pause
