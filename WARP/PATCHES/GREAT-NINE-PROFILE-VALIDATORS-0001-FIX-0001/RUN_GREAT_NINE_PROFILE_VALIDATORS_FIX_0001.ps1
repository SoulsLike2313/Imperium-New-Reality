$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"

Write-Host "== GREAT-NINE-PROFILE-VALIDATORS-0001-FIX-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) {
  throw "FILES_TO_LAND not found: $FilesToLand"
}

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Write-Host "Slot .gitkeep fix applied."

$OriginalRunner = Join-Path $RepoRoot "WARP\PATCHES\GREAT-NINE-PROFILE-VALIDATORS-0001\RUN_GREAT_NINE_PROFILE_VALIDATORS.ps1"

if (-not (Test-Path $OriginalRunner)) {
  throw "Original runner not found: $OriginalRunner"
}

Write-Host ""
Write-Host "Rerunning original Great Nine profile validators..."
pwsh $OriginalRunner
if ($LASTEXITCODE -ne 0) {
  throw "Original Great Nine profile validators failed after slot fix with exit code $LASTEXITCODE"
}

Write-Host "GREAT NINE PROFILE VALIDATORS FIX-0001 PASS"
