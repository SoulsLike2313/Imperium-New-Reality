$ErrorActionPreference = "Stop"
$PatchId = "MECHANICUS-RESIDENCY-TRUST-GATE-0001"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "../../..")
$FilesToLand = Join-Path $ScriptDir "FILES_TO_LAND"

$ver = $PSVersionTable.PSVersion.ToString()
if ($ver -ne "7.6.2") {
  Write-Host "IMPERIUM SHELL: pwsh $ver (expected 7.6.2)" -ForegroundColor Yellow
} else {
  Write-Host "IMPERIUM SHELL: pwsh 7.6.2 OK" -ForegroundColor Green
}
Write-Host "IMPERIUM SHELL: pwsh $ver OK" -ForegroundColor Green
Write-Host "== $PatchId =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND missing: $FilesToLand" }
Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

$Validator = Join-Path $RepoRoot "ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_residency_trust_gate.py"
python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) {
  throw "Mechanicus residency trust gate failed with exit code $LASTEXITCODE"
}
Write-Host "MECHANICUS RESIDENCY TRUST GATE PASS" -ForegroundColor Green
