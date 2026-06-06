@echo off
setlocal
cd /d "%~dp0"

where wt >nul 2>nul
if errorlevel 1 (
  call "%~dp0LAUNCH_MECHANICUS_FORGE_CLIENT_V1_0.cmd"
  exit /b %errorlevel%
)

start "" wt -w 0 nt --title "Mechanicus Forge Client V1.0" cmd /k "cd /d %~dp0 && py -3 mechanicus_forge_client_v1_0_no_fake_heraldry.py"
