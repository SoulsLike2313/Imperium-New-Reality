$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\ASTRONOMICON\VALIDATORS\validate_patch_pack_lifecycle_validation_foundation.py"

Write-Host "== PATCH-PACK-LIFECYCLE-VALIDATION-FOUNDATION-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\INQUISITION\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Patch Pack lifecycle validation foundation failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\INQUISITION\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "PATCH PACK LIFECYCLE VALIDATION FOUNDATION PASS"
