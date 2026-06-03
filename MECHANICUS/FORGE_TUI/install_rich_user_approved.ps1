param()

$ErrorActionPreference = "Stop"

Write-Host "=== OWNER-APPROVED USER INSTALL: rich ===" -ForegroundColor Yellow
Write-Host "This installs only Python package 'rich' into the current user environment." -ForegroundColor Yellow
Write-Host "No registry/capability cards are changed by this helper." -ForegroundColor Yellow

py -3 -m pip install --user rich
py -3 -c "import rich; print('rich ok')"
