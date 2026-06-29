$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\THRONE\VALIDATORS\validate_throne_self_form.py"

Write-Host "== THRONE-CROWN-ORGAN-FOUNDATION-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) {
  throw "FILES_TO_LAND not found: $FilesToLand"
}

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force (Join-Path $RepoRoot "ORGANS\THRONE\VALIDATORS\__pycache__") -ErrorAction SilentlyContinue

if (-not (Test-Path $Validator)) {
  throw "Throne self validator not found after copy: $Validator"
}

python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) {
  throw "Throne self-form validation failed with exit code $LASTEXITCODE"
}

Remove-Item -Recurse -Force (Join-Path $RepoRoot "ORGANS\THRONE\VALIDATORS\__pycache__") -ErrorAction SilentlyContinue

Write-Host "THRONE CROWN ORGAN FOUNDATION PASS"
