$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\validate_mechanicus_strict_build_lane_validator_false_negative_hotfix.py"

Write-Host "== MECHANICUS-STRICT-BUILD-LANE-VALIDATOR-FALSE-NEGATIVE-HOTFIX-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) {
  throw "FILES_TO_LAND not found: $FilesToLand"
}

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\TOOLS\__pycache__" -ErrorAction SilentlyContinue

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) {
  throw "Mechanicus strict build lane validator false-negative hotfix failed with exit code $LASTEXITCODE"
}

Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\TOOLS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "MECHANICUS STRICT BUILD LANE VALIDATOR FALSE NEGATIVE HOTFIX PASS"
