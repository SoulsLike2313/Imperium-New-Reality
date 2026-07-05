$ErrorActionPreference = "Stop"

$ExpectedPwsh = "7.6.2"
$ActualPwsh = $PSVersionTable.PSVersion.ToString()
if ($ActualPwsh -eq $ExpectedPwsh) {
  Write-Host "IMPERIUM SHELL: pwsh $ActualPwsh OK" -ForegroundColor Green
} else {
  Write-Host "IMPERIUM SHELL: pwsh $ActualPwsh (expected $ExpectedPwsh)" -ForegroundColor Yellow
}

$PatchId = "MECHANICUS-CURRENT-TRUTH-RECEIPTS-GATE-0001"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "../../..")
$FilesToLand = Join-Path $ScriptDir "FILES_TO_LAND"

Write-Host "== $PatchId =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) {
  throw "FILES_TO_LAND not found: $FilesToLand"
}

Get-ChildItem -LiteralPath $FilesToLand | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination $RepoRoot -Recurse -Force
}

$Validator = Join-Path $RepoRoot "ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_current_truth_receipts_gate.py"
python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) {
  throw "Mechanicus current truth receipts gate failed with exit code $LASTEXITCODE"
}

Write-Host "MECHANICUS CURRENT TRUTH RECEIPTS GATE PASS" -ForegroundColor Green
