$ErrorActionPreference = "Stop"

$ExpectedPwsh = "7.6.2"
$ActualPwsh = $PSVersionTable.PSVersion.ToString()
if ($ActualPwsh -ne $ExpectedPwsh) {
  throw "IMPERIUM SHELL REJECTED: expected pwsh $ExpectedPwsh, got $ActualPwsh"
}
Write-Host "IMPERIUM SHELL: pwsh $ActualPwsh OK"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\validate_mechanicus_organ_readiness_rollup.py"

Write-Host "== MECHANICUS-ORGAN-READINESS-ROLLUP-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) {
  throw "FILES_TO_LAND not found: $FilesToLand"
}

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force (Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\__pycache__") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $RepoRoot "ORGANS\MECHANICUS\TOOLS\__pycache__") -ErrorAction SilentlyContinue

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) {
  throw "Mechanicus organ readiness rollup failed with exit code $LASTEXITCODE"
}

Remove-Item -Recurse -Force (Join-Path $RepoRoot "ORGANS\MECHANICUS\VALIDATORS\__pycache__") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $RepoRoot "ORGANS\MECHANICUS\TOOLS\__pycache__") -ErrorAction SilentlyContinue

Write-Host "MECHANICUS ORGAN READINESS ROLLUP PASS"
