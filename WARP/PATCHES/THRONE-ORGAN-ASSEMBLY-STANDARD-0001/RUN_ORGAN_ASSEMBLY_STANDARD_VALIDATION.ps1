$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\THRONE\VALIDATORS\validate_organ_assembly_standard.py"

Write-Host "== THRONE-ORGAN-ASSEMBLY-STANDARD-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

if (-not (Test-Path $Validator)) { throw "Validator not found after copy: $Validator" }

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Organ assembly standard validation failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "THRONE ORGAN ASSEMBLY STANDARD PASS"
