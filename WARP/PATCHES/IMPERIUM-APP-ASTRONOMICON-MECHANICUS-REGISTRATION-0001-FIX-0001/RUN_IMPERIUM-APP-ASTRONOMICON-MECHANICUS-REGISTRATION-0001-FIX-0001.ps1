$ErrorActionPreference = "Stop"
$PatchId = "IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001-FIX-0001"
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

$Validator = Join-Path $RepoRoot "SUPPORT/APP_TAURI/tests/validate_astronomicon_mechanicus_registration_picker_fix.py"
python $Validator --repo-root $RepoRoot --host-build-check
if ($LASTEXITCODE -ne 0) { throw "$PatchId failed with exit code $LASTEXITCODE" }
Write-Host "IMPERIUM APP ASTRONOMICON PATCH PICKER FIX PASS" -ForegroundColor Green
