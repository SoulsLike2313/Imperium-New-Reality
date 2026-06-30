$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) { throw "Run from repo root." }

Write-Host "Run:"
Write-Host "pwsh WARP/PATCHES/ROOT-TRANSPORT-CLUTTER-RELOCATION-0001/RUN_ROOT_TRANSPORT_CLUTTER_RELOCATION.ps1"
