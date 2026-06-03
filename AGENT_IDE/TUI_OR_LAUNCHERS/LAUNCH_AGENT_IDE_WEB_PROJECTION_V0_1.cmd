@echo off
setlocal
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%\..\..\.."
python IMPERIUM_NEW_GENERATION\AGENT_IDE\WEB_PROJECTION\agent_ide_web_projection_server_v0_1.py --host 127.0.0.1 --port 4173 %*
popd
endlocal
