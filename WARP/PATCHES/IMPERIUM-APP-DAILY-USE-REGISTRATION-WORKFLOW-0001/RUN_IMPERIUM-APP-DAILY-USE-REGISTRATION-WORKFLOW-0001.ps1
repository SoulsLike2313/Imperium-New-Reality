$ErrorActionPreference = "Stop"
$PatchId = "IMPERIUM-APP-DAILY-USE-REGISTRATION-WORKFLOW-0001"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "../../..")
$FilesToLand = Join-Path $ScriptDir "FILES_TO_LAND"

$ver = $PSVersionTable.PSVersion.ToString()
if ($ver -ne "7.6.2") {
  Write-Host "IMPERIUM SHELL: pwsh $ver (expected 7.6.2)" -ForegroundColor Yellow
} else {
  Write-Host "IMPERIUM SHELL: pwsh 7.6.2 OK" -ForegroundColor Green
}

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND missing: $FilesToLand" }
Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

$Validator = Join-Path $RepoRoot "SUPPORT/APP_TAURI/tests/validate_two_phase_organ_registration.py"
python $Validator --repo-root $RepoRoot --host-build-check
if ($LASTEXITCODE -ne 0) { throw "$PatchId failed with exit code $LASTEXITCODE" }
Write-Host "IMPERIUM APP DAILY USE REGISTRATION WORKFLOW PASS" -ForegroundColor Green
