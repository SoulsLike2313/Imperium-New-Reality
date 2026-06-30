$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) { throw "Run from repo root." }

Write-Host "Run:"
Write-Host "pwsh WARP/PATCHES/THRONE-TARGET-GAP-ORGAN-IMPLEMENTATION-SPLIT-0001/RUN_THRONE_TARGET_GAP_ORGAN_IMPLEMENTATION_SPLIT.ps1"
