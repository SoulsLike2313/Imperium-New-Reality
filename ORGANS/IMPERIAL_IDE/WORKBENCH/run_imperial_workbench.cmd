@echo off
REM IMPERIAL IDE :: MECHANICUS WORKBENCH launcher (cmd fallback)
REM Use this if PowerShell execution policy blocks the .ps1 launcher.
REM Usage:  run_imperial_workbench.cmd [gui^|tui]
setlocal
set SURFACE=%1
if "%SURFACE%"=="" set SURFACE=gui

where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=python3)

echo.
echo   * IMPERIAL IDE :: MECHANICUS WORKBENCH  (surface=%SURFACE%)
echo.

if /I "%SURFACE%"=="tui" (
    "%PY%" "%~dp0TUI\imperial_tui.py"
) else (
    "%PY%" "%~dp0GUI\imperial_gui_workbench.py"
)
endlocal
