$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\THRONE\VALIDATORS\validate_post_astronomicon_score_readout.py"

Write-Host "== POST-ASTRONOMICON-SCORE-READOUT-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Write-Host "== Refreshing measured score sources =="

$RefreshScripts = @(
  "WARP\PATCHES\IMPERIUM-POPULATION-CENSUS-REFRESH-0001\RUN_IMPERIUM_POPULATION_CENSUS_REFRESH.ps1",
  "WARP\PATCHES\THRONE-TARGET-GAP-ORGAN-IMPLEMENTATION-SPLIT-0001\RUN_THRONE_TARGET_GAP_ORGAN_IMPLEMENTATION_SPLIT.ps1",
  "WARP\PATCHES\THRONE-ORGAN-ASSEMBLY-STAGE-SCORING-INTEGRATION-0001\RUN_ORGAN_ASSEMBLY_STAGE_SCORING.ps1"
)

foreach ($rel in $RefreshScripts) {
  $script = Join-Path $RepoRoot $rel
  if (-not (Test-Path $script)) {
    throw "Required refresh script missing: $rel"
  }
  Write-Host "RUN: $rel"
  pwsh $script
  if ($LASTEXITCODE -ne 0) {
    throw "Refresh script failed: $rel"
  }
}

Remove-Item -Recurse -Force "ORGANS\THRONE\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Post Astronomicon score readout validation failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\THRONE\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "POST ASTRONOMICON SCORE READOUT PASS"
