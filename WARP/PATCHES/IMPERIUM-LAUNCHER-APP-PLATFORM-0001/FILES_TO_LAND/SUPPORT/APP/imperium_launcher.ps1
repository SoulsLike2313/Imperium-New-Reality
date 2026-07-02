param(
  [switch]$SelfTest
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$App = Join-Path $RepoRoot "SUPPORT\APP\imperium_launcher_app.ps1"

if ($SelfTest) {
  pwsh $App -SelfTest
  exit $LASTEXITCODE
}

pwsh $App
exit $LASTEXITCODE
