param(
    [string]$Category = "UTILITIES",
    [string]$Select = "",
    [int]$Limit = 15
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== MECHANICUS FORGE TUI V0.1: DEP CHECK ===" -ForegroundColor Cyan
py -3 -c "import rich; print('rich ok')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "MISSING DEP: rich" -ForegroundColor Yellow
    Write-Host "Run this only if Owner approves local user-package install:" -ForegroundColor Yellow
    Write-Host "py -3 -m pip install --user rich" -ForegroundColor Cyan
    throw "Dependency missing: rich"
}

Write-Host "=== START READ-ONLY SNAPSHOT ===" -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($Select)) {
    py -3 "$PSScriptRoot\mechanicus_forge_tui_v0_1.py" --category $Category --limit $Limit
} else {
    py -3 "$PSScriptRoot\mechanicus_forge_tui_v0_1.py" --category $Category --select $Select --limit $Limit
}
