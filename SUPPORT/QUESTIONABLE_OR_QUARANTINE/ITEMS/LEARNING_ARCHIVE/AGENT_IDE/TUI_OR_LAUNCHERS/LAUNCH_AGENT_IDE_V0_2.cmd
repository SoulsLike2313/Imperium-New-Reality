@echo off
setlocal
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%\..\..\.."
python IMPERIUM_NEW_GENERATION\AGENT_IDE\APP\agent_ide_app_v0_2.py %*
popd
endlocal
