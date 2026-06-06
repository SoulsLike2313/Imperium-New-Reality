@echo off
setlocal
cd /d "%~dp0\..\..\.."
python IMPERIUM_NEW_GENERATION\ADMINISTRATUM\TUI\administratum_tui_v0_1.py %*
if errorlevel 1 (
  echo ADMINISTRATUM_TUI_STATUS=FAIL
  exit /b %errorlevel%
)
echo ADMINISTRATUM_TUI_STATUS=PASS
endlocal
