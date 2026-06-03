@echo off
setlocal
cd /d "%~dp0"

title Mechanicus Forge Client V1.0

echo === MECHANICUS FORGE CLIENT V1.0 NO FAKE HERALDRY ===
echo Location: %CD%
echo.

py -3 -c "import rich, textual; print('deps ok')" 1>nul 2>nul
if errorlevel 1 (
  echo MISSING PYTHON DEPENDENCIES: rich/textual
  echo.
  echo Run this OWNER-APPROVED command first:
  echo py -3 -m pip install --user rich textual
  echo.
  pause
  exit /b 1
)

py -3 "%~dp0mechanicus_forge_client_v1_0_no_fake_heraldry.py"
echo.
echo Client exited.
pause
