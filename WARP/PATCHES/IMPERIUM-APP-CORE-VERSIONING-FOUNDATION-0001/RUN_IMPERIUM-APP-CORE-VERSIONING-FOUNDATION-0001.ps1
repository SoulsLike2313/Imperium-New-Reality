param([switch]$VerboseJson)
$ErrorActionPreference = "Stop"
function Find-RepoRoot {
  $cur = (Get-Location).Path
  while ($true) {
    if ((Test-Path (Join-Path $cur "ORGANS")) -and (Test-Path (Join-Path $cur "WARP"))) { return $cur }
    $parent = Split-Path $cur -Parent
    if ($parent -eq $cur -or [string]::IsNullOrWhiteSpace($parent)) { throw "Repo root not found" }
    $cur = $parent
  }
}
$RepoRoot = Find-RepoRoot
$expected = "7.6.2"
$actual = $PSVersionTable.PSVersion.ToString()
if ($actual -ne $expected) { Write-Host "IMPERIUM SHELL: pwsh $actual (expected $expected)" -ForegroundColor Yellow } else { Write-Host "IMPERIUM SHELL: pwsh $actual OK" -ForegroundColor Green }
$FilesToLand = Join-Path $RepoRoot "WARP/PATCHES/IMPERIUM-APP-CORE-VERSIONING-FOUNDATION-0001/FILES_TO_LAND"
Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force
$validator = Join-Path $RepoRoot "SUPPORT/APP_TAURI/tests/validate_imperium_core_versioning_foundation.py"
$args = @($validator, "--repo-root", $RepoRoot, "--apply")
if ($VerboseJson) { $args += "--json" }
python @args
if ($LASTEXITCODE -ne 0) { throw "IMPERIUM-APP-CORE-VERSIONING-FOUNDATION-0001 failed with exit code $LASTEXITCODE" }
