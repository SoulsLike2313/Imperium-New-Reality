$ErrorActionPreference = "Stop"

$Required = [Version]"7.6.2"
$Actual = $PSVersionTable.PSVersion
if ($Actual -ne $Required) {
  throw "IMPERIUM SHELL: expected pwsh 7.6.2, got $Actual"
}
Write-Host "IMPERIUM SHELL: pwsh 7.6.2 OK" -ForegroundColor Green

$ScriptPath = $MyInvocation.MyCommand.Path
$PatchDir = Split-Path -Parent $ScriptPath
$RepoRoot = Resolve-Path (Join-Path $PatchDir "../../..")
$FilesToLand = Join-Path $PatchDir "FILES_TO_LAND"

Write-Host "== CUSTODES-MECHANICUS-PROSECUTOR-GATE-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

$Validator = Join-Path $RepoRoot "ORGANS/CUSTODES/VALIDATORS/validate_custodes_mechanicus_prosecutor_gate.py"
if (-not (Test-Path $Validator)) {
  $ValidatorSource = Join-Path $FilesToLand "ORGANS/CUSTODES/VALIDATORS/validate_custodes_mechanicus_prosecutor_gate.py"
  $ValidatorParent = Split-Path -Parent $Validator
  if (-not (Test-Path $ValidatorParent)) { New-Item -ItemType Directory -Path $ValidatorParent -Force | Out-Null }
  Copy-Item -Path $ValidatorSource -Destination $Validator -Force
}

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) {
  throw "Custodes Mechanicus prosecutor gate failed with exit code $LASTEXITCODE"
}

Write-Host "CUSTODES MECHANICUS PROSECUTOR GATE PASS" -ForegroundColor Green
