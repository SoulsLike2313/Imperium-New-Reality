$ErrorActionPreference = "Stop"
if (-not (Test-Path ".git")) { throw "Run from repository root." }
$PatchDir = "WARP\PATCHES\IMPERIUM-POPULATION-CENSUS-0001"
if (-not (Test-Path $PatchDir)) { throw "Patch dir not found after extraction: $PatchDir" }
Write-Host "Patch present: $PatchDir"
Write-Host "Run: pwsh WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/RUN_POPULATION_CENSUS.ps1"
