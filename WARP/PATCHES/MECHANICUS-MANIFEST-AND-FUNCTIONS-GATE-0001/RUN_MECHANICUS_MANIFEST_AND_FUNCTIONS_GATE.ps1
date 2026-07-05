$ErrorActionPreference = "Stop"

$ExpectedPwsh = "7.6.2"
$ActualPwsh = $PSVersionTable.PSVersion.ToString()
if ($ActualPwsh -eq $ExpectedPwsh) {
  Write-Host "IMPERIUM SHELL: pwsh $ActualPwsh OK" -ForegroundColor Green
} else {
  Write-Host "IMPERIUM SHELL: pwsh $ActualPwsh (expected $ExpectedPwsh)" -ForegroundColor Yellow
}

$PatchId = "MECHANICUS-MANIFEST-AND-FUNCTIONS-GATE-0001"
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

$Validator = Join-Path $RepoRoot "ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_manifest_and_functions_gate.py"
python $Validator --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) {
  throw "Mechanicus manifest/functions gate failed with exit code $LASTEXITCODE"
}

Write-Host "MECHANICUS MANIFEST AND FUNCTIONS GATE PASS" -ForegroundColor Green
