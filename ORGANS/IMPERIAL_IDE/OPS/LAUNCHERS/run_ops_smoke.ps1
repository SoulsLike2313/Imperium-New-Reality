# run_ops_smoke.ps1 - run the operational engine smoke test on PC.
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..\..").Path
$env:IMPERIUM_ROOT = $RepoRoot
$Smoke = Join-Path $RepoRoot "ORGANS\IMPERIAL_IDE\OPS\TESTS\ops_smoke.py"
if (-Not (Test-Path $Smoke)) {
    $Smoke = Join-Path $PSScriptRoot "..\TESTS\ops_smoke.py"
}
Write-Host "Running operational smoke..."
python $Smoke
if ($LASTEXITCODE -ne 0) {
    Write-Error "SMOKE FAILED (exit $LASTEXITCODE)"
    exit $LASTEXITCODE
}
Write-Host "SMOKE PASS"
