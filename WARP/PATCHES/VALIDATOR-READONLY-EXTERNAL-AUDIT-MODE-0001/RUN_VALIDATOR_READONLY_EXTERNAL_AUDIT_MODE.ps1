$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$MechanicusValidator = Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\validate_validator_readonly_modes.py"
Write-Host "== VALIDATOR-READONLY-EXTERNAL-AUDIT-MODE-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"
if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }
Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
if (-not (Test-Path $MechanicusValidator)) { throw "Mechanicus validator not found after copy: $MechanicusValidator" }
python $MechanicusValidator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Validator readonly external audit mode proof failed with exit code $LASTEXITCODE" }
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Write-Host "VALIDATOR READONLY EXTERNAL AUDIT MODE PASS"
