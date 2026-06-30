$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) { throw "Run from repo root." }

Write-Host "Run:"
Write-Host "pwsh WARP/PATCHES/EXTERNAL-AUDIT-CONTROL-AND-CONSOLIDATION-0001/RUN_EXTERNAL_AUDIT_CONTROL_AND_CONSOLIDATION.ps1"
