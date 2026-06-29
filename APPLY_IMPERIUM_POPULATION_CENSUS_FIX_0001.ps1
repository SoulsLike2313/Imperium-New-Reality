$ErrorActionPreference = "Stop"
$Repo = Get-Location
Write-Host "Installing IMPERIUM-POPULATION-CENSUS-0001-FIX-0001 into: $Repo"
if (-not (Test-Path ".git")) { throw "Run this from repository root." }
$FixDir = "WARP\PATCHES\IMPERIUM-POPULATION-CENSUS-0001-FIX-0001"
$ParentDir = "WARP\PATCHES\IMPERIUM-POPULATION-CENSUS-0001"
if (-not (Test-Path $FixDir)) { throw "Fix dir not found after extraction: $FixDir" }
if (-not (Test-Path $ParentDir)) { throw "Parent census dir not found: $ParentDir" }
Remove-Item -Recurse -Force "$ParentDir\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$ParentDir\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Write-Host "Run fixed census:"
Write-Host "pwsh WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001-FIX-0001/RUN_FIX_AND_CENSUS.ps1"
