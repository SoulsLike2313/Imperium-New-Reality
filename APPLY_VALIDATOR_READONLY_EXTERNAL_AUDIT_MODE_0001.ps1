$ErrorActionPreference = "Stop"
if (-not (Test-Path ".git")) { throw "Run from repo root." }
Write-Host "Run:"
Write-Host "pwsh WARP/PATCHES/VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001/RUN_VALIDATOR_READONLY_EXTERNAL_AUDIT_MODE.ps1"
