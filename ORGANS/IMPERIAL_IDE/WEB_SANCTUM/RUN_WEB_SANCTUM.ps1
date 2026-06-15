param([string]$RepoRoot=(Resolve-Path "$PSScriptRoot\..\..\..").Path,[int]$Port=8792)
$ErrorActionPreference="Stop"
Write-Host "Starting Web Sanctum V0.8.1 read-only shell" -ForegroundColor Cyan
Write-Host "Actions disabled. Use RUN_WEB_SANCTUM_ACTIONS.ps1 for allowlisted local actions." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:$Port/" | Out-Null
python "$PSScriptRoot\tools\local_bridge.py" --repo-root $RepoRoot --port $Port
