$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$Builder = Join-Path $PSScriptRoot "TOOLS\build_population_census.py"
$Validator = Join-Path $PSScriptRoot "VALIDATORS\validate_population_census.py"
Write-Host "== IMPERIUM-POPULATION-CENSUS-0001 =="
Write-Host "Repo root: $RepoRoot"
python $Builder --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Population census builder failed: $LASTEXITCODE" }
python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Population census validator failed: $LASTEXITCODE" }
Write-Host "Population census PASS"
