param([string]$RepoRoot=(Resolve-Path "$PSScriptRoot\..\..\..").Path,[int]$Port=8792)
$ErrorActionPreference="Stop"
Write-Host "Starting Web Sanctum V0.8.1 with stage loop polish + allowlisted job runner" -ForegroundColor Cyan
Write-Host "No arbitrary shell endpoint exists. Git commit/push are not exposed." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:$Port/" | Out-Null
python "$PSScriptRoot\tools\local_bridge.py" --repo-root $RepoRoot --port $Port --actions
