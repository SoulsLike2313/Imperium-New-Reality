param()

$ErrorActionPreference = "Stop"

Write-Host "=== OWNER-APPROVED USER INSTALL: rich + textual ===" -ForegroundColor Yellow
Write-Host "This installs Python packages only into the current user environment." -ForegroundColor Yellow
Write-Host "No IMPERIUM registry/capability cards are changed by this helper." -ForegroundColor Yellow

py -3 -m pip install --user rich textual
py -3 -c "import rich, textual; print('deps ok')"
