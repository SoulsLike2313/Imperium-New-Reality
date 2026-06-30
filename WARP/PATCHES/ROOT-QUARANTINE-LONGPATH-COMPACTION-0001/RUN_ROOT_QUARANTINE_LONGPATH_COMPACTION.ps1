$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\validate_root_quarantine_longpath_compaction.py"

Write-Host "== ROOT-QUARANTINE-LONGPATH-COMPACTION-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

if (-not (Test-Path $Validator)) { throw "Validator not found after copy: $Validator" }

python $Validator --repo-root $RepoRoot --apply --max-rel-path 180 --max-full-path 220
if ($LASTEXITCODE -ne 0) { throw "Root quarantine longpath compaction failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "ROOT QUARANTINE LONGPATH COMPACTION PASS"
