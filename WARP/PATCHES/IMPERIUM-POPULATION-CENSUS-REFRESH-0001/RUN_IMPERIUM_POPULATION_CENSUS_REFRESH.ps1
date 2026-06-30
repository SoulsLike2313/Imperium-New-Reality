$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\ADMINISTRATUM\VALIDATORS\validate_population_census_refresh.py"

Write-Host "== IMPERIUM-POPULATION-CENSUS-REFRESH-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\ADMINISTRATUM\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

if (-not (Test-Path $Validator)) { throw "Validator not found after copy: $Validator" }

python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Population census refresh failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\ADMINISTRATUM\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "IMPERIUM POPULATION CENSUS REFRESH PASS"
