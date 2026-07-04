$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\validate_mechanicus_cockpit_patch_registry_and_language_codex.py"

Write-Host "== MECHANICUS-COCKPIT-PATCH-REGISTRY-AND-LANGUAGE-CODEX-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"
if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }
Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Mechanicus cockpit patch registry and language codex validator failed with exit code $LASTEXITCODE" }
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Write-Host "MECHANICUS COCKPIT PATCH REGISTRY AND LANGUAGE CODEX PASS"
