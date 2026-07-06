param(
  [switch]$VerboseJson
)
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$Expected = "7.6.2"
$Actual = $PSVersionTable.PSVersion.ToString()
if ($Actual -ne $Expected) { throw "IMPERIUM SHELL expected pwsh $Expected, got $Actual" }
Write-Host "IMPERIUM SHELL: pwsh $Actual OK" -ForegroundColor Green
Write-Host "TASK: IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001"

$Validator = Join-Path $RepoRoot "WARP/PATCHES/IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001/FILES_TO_LAND/SUPPORT/APP_TAURI/tests/validate_astronomicon_mechanicus_registration.py"
$Args = @($Validator, "--repo-root", $RepoRoot, "--apply", "--host-build-check")
if ($VerboseJson) { $Args += "--verbose-json" }
python @Args
if ($LASTEXITCODE -ne 0) { throw "IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001 failed with exit code $LASTEXITCODE" }
Write-Host "IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001 PASS" -ForegroundColor Green
