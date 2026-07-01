$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\ASTRONOMICON\VALIDATORS\validate_astronomicon_dry_run_and_launcher.py"

Write-Host "== IMPERIUM-LAUNCHER-ASTRONOMICON-DRY-RUN-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }
Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "SUPPORT\LAUNCHER\__pycache__" -ErrorAction SilentlyContinue

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Astronomicon dry-run / launcher validation failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "SUPPORT\LAUNCHER\__pycache__" -ErrorAction SilentlyContinue

Write-Host "IMPERIUM LAUNCHER + ASTRONOMICON DRY-RUN PASS"
