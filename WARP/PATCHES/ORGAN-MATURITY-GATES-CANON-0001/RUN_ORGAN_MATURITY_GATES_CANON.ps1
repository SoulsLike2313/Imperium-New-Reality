$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"

Write-Host "== ORGAN-MATURITY-GATES-CANON-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\DOCTRINARIUM\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\CUSTODES\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

python "ORGANS\DOCTRINARIUM\VALIDATORS\validate_organ_maturity_gates_canon.py" --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Doctrinarium organ maturity gates canon validator failed with exit code $LASTEXITCODE" }

python "ORGANS\CUSTODES\VALIDATORS\validate_organ_maturity_prosecutor_matrix.py" --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Custodes organ maturity prosecutor matrix validator failed with exit code $LASTEXITCODE" }

python "ORGANS\THRONE\VALIDATORS\validate_organ_maturity_crown_gate_matrix.py" --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Throne organ maturity crown gate matrix validator failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\DOCTRINARIUM\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\CUSTODES\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "ORGAN MATURITY GATES CANON PASS"
