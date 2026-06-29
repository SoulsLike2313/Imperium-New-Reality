$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$Parent = Join-Path $RepoRoot "WARP\PATCHES\IMPERIUM-POPULATION-CENSUS-0001"
$Builder = Join-Path $Parent "TOOLS\build_population_census.py"
$Validator = Join-Path $Parent "VALIDATORS\validate_population_census.py"
Write-Host "== IMPERIUM-POPULATION-CENSUS-0001-FIX-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Parent census pack: $Parent"
Remove-Item -Recurse -Force (Join-Path $Parent "TOOLS\__pycache__") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $Parent "VALIDATORS\__pycache__") -ErrorAction SilentlyContinue
if (-not (Test-Path $Builder)) { throw "Builder not found: $Builder" }
if (-not (Test-Path $Validator)) { throw "Validator not found: $Validator" }
python $Builder --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Fixed population census builder failed with exit code $LASTEXITCODE" }
Remove-Item -Recurse -Force (Join-Path $Parent "TOOLS\__pycache__") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $Parent "VALIDATORS\__pycache__") -ErrorAction SilentlyContinue
python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Fixed population census validator failed with exit code $LASTEXITCODE" }
Remove-Item -Recurse -Force (Join-Path $Parent "TOOLS\__pycache__") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $Parent "VALIDATORS\__pycache__") -ErrorAction SilentlyContinue
Write-Host "Population census FIX PASS"
