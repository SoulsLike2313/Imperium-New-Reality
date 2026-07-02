@echo off
setlocal
cd /d "%~dp0\..\.."
pwsh SUPPORT\APP\imperium_launcher.ps1
endlocal
