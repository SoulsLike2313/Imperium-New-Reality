$ErrorActionPreference = "Stop"

$Repo = Get-Location
Write-Host "Installing THRONE-TARGET-GAP-VALIDATOR-0001 into: $Repo"

if (-not (Test-Path ".git")) {
  throw "Run this from repository root."
}

$PatchDir = "WARP\PATCHES\THRONE-TARGET-GAP-VALIDATOR-0001"
if (-not (Test-Path $PatchDir)) {
  throw "Patch dir not found after extraction: $PatchDir"
}

Write-Host "Patch present: $PatchDir"
Write-Host ""
Write-Host "Run:"
Write-Host "pwsh WARP/PATCHES/THRONE-TARGET-GAP-VALIDATOR-0001/RUN_THRONE_TARGET_GAP_VALIDATION.ps1"
