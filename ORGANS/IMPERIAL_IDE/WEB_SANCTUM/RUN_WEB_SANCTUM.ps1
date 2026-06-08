param([string]$RepoRoot=(Resolve-Path "$PSScriptRoot\..\..\..").Path,[int]$Port=8790)
$ErrorActionPreference="Stop"
Write-Host "Starting Web Sanctum V0.5 read-only/static bridge" -ForegroundColor Cyan
python "$PSScriptRoot\tools\local_bridge.py" --repo-root $RepoRoot --port $Port
