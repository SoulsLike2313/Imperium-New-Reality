$ErrorActionPreference = "Stop"
if (-not (Test-Path ".git")) { throw "Run from repo root" }
Write-Host "Run:"
Write-Host "pwsh WARP/PATCHES/GREAT-NINE-PROFILE-VALIDATORS-0001/RUN_GREAT_NINE_PROFILE_VALIDATORS.ps1"
