$ErrorActionPreference = "Stop"

$Repo = Get-Location
Write-Host "Installing THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001-FIX-0002 into: $Repo"

if (-not (Test-Path ".git")) { throw "Run this from repository root." }

$PatchDir = "WARP\PATCHES\THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001-FIX-0002"
if (-not (Test-Path $PatchDir)) { throw "Patch dir not found after extraction: $PatchDir" }

Write-Host "Run:"
Write-Host "pwsh WARP/PATCHES/THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001-FIX-0002/RUN_THRONE_TARGET_GAP_CORE_V1_SCORING_FIX_0002.ps1"
