@echo off
setlocal
python "%~dp0officio_agentis_tui_v0_1.py" --mode summary --strict
set EXIT_CODE=%ERRORLEVEL%
echo.
if %EXIT_CODE%==0 (
  echo OFFICIO_AGENTIS_TUI_STATUS=PASS
) else (
  echo OFFICIO_AGENTIS_TUI_STATUS=FAIL
)
exit /b %EXIT_CODE%
