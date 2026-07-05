$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\validate_mechanicus_language_surface_v2_toolchain_probe_ultrasafe_hotfix.py"
Write-Host "== MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-PROBE-ULTRASAFE-HOTFIX-0002 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"
if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }
Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\TOOLS\__pycache__" -ErrorAction SilentlyContinue
python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Mechanicus language surface v2 toolchain probe ultrasafe hotfix failed with exit code $LASTEXITCODE" }
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\MECHANICUS\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Write-Host "MECHANICUS LANGUAGE SURFACE V2 TOOLCHAIN PROBE ULTRASAFE HOTFIX PASS"
