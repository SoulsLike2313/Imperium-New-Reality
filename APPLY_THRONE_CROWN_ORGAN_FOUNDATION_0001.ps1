$ErrorActionPreference = "Stop"

$Repo = Get-Location
Write-Host "Installing THRONE-CROWN-ORGAN-FOUNDATION-0001 into: $Repo"

if (-not (Test-Path ".git")) {
  throw "Run this from repository root."
}

$PatchDir = "WARP\PATCHES\THRONE-CROWN-ORGAN-FOUNDATION-0001"
if (-not (Test-Path $PatchDir)) {
  throw "Patch dir not found after extraction: $PatchDir"
}

Write-Host "Patch present: $PatchDir"
Write-Host ""
Write-Host "Run Throne foundation:"
Write-Host "pwsh WARP/PATCHES/THRONE-CROWN-ORGAN-FOUNDATION-0001/RUN_THRONE_CROWN_ORGAN_FOUNDATION.ps1"
