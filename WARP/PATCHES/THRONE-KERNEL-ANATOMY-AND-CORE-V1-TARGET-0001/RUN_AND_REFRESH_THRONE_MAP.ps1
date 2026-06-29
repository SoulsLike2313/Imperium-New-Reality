$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Write-Host "== THRONE KERNEL ANATOMY + REFRESH THRONE MAP =="

pwsh (Join-Path $PSScriptRoot "RUN_THRONE_KERNEL_ANATOMY_VALIDATION.ps1")

$CensusRunner = Join-Path $RepoRoot "WARP\PATCHES\IMPERIUM-POPULATION-CENSUS-0001-FIX-0001\RUN_FIX_AND_CENSUS.ps1"
$GapRunner = Join-Path $RepoRoot "WARP\PATCHES\THRONE-TARGET-GAP-VALIDATOR-0001\RUN_THRONE_TARGET_GAP_VALIDATION.ps1"

if (Test-Path $CensusRunner) {
  Write-Host ""
  Write-Host "Refreshing population census..."
  pwsh $CensusRunner
} else {
  Write-Host "Population census runner not found, skipping: $CensusRunner"
}

if (Test-Path $GapRunner) {
  Write-Host ""
  Write-Host "Refreshing Throne target gap..."
  pwsh $GapRunner
} else {
  Write-Host "Throne target gap runner not found, skipping: $GapRunner"
}

Write-Host "THRONE MAP REFRESH DONE"
