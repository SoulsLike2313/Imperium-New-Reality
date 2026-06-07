[CmdletBinding()]
param(
  [switch]$Smoke,
  [string]$Root = $env:IMPERIUM_ROOT
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Launcher = Join-Path $RepoRoot 'ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py'
if ($Root) { $env:IMPERIUM_ROOT = $Root }
Push-Location $RepoRoot
try {
  if ($Smoke) { & python $Launcher --smoke } else { & python $Launcher }
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
