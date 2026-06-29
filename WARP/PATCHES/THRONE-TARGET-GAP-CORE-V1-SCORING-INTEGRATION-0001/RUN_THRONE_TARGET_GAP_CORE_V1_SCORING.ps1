$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\THRONE\VALIDATORS\validate_throne_target_gap.py"

Write-Host "== THRONE-TARGET-GAP-CORE-V1-SCORING-INTEGRATION-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) {
  throw "FILES_TO_LAND not found: $FilesToLand"
}

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

if (-not (Test-Path $Validator)) {
  throw "Validator not found after copy: $Validator"
}

python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) {
  throw "Throne target gap Core v1 scoring validator failed with exit code $LASTEXITCODE"
}

Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "THRONE TARGET GAP CORE V1 SCORING PASS"
