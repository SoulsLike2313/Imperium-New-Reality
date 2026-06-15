@echo off
setlocal
cd /d "%~dp0"

where wt >nul 2>nul
if errorlevel 1 (
  call "%~dp0LAUNCH_MECHANICUS_FORGE_CLIENT_V0_5_RU.cmd"
  exit /b %errorlevel%
)

start "" wt -w 0 nt --title "Mechanicus Forge Client V0.5 RU" cmd /k "cd /d %~dp0 && py -3 mechanicus_forge_client_v0_5_ru.py"
