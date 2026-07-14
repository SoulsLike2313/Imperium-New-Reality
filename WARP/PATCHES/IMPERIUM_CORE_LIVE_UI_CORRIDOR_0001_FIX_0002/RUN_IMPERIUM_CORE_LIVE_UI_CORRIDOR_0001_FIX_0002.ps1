$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002'
$ExpectedHead = '8f34f78f6dc36b82989ac51e2e2baedba26872de'
$ExpectedRealityHead = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$PatchRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PayloadRoot = Join-Path $PatchRoot 'payload'
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$BaselinePath = Join-Path $PatchRoot 'runtime/LIVE_UI_BASELINE.json'
$CorridorReportRel = 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$HardeningReportRel = 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'

function Invoke-Git([string]$Repo, [string[]]$Arguments) {
    $output = & git -C $Repo @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git $($Arguments -join ' ') failed: $output" }
    return ($output -join "`n").Trim()
}
function Restore-Payload([string]$Repo, $Manifest) {
    foreach ($entry in $Manifest.preimages) {
        $backup = Join-Path $BackupRoot $entry.path
        $target = Join-Path $Repo $entry.path
        if (Test-Path -LiteralPath $backup) { Copy-Item -LiteralPath $backup -Destination $target -Force }
    }
    foreach ($entry in $Manifest.added_files) {
        $target = Join-Path $Repo $entry
        if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
    }
    $registryBackup = Join-Path $BackupRoot "$CorridorReportRel/CAPABILITY_REGISTRY.json"
    $registryTarget = Join-Path $Repo "$CorridorReportRel/CAPABILITY_REGISTRY.json"
    if (Test-Path -LiteralPath $registryBackup) { Copy-Item -LiteralPath $registryBackup -Destination $registryTarget -Force }
}

$Repo = [System.IO.Path]::GetFullPath((Invoke-Git (Get-Location).Path @('rev-parse','--show-toplevel')))
$Reality = 'E:\IMPERIUM_REALITY'
if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw "BLOCK_PWSH_VERSION: $($PSVersionTable.PSVersion)" }
if ((Invoke-Git $Repo @('rev-parse','HEAD')) -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
if ((Invoke-Git $Repo @('rev-parse','--abbrev-ref','HEAD')) -ne $ExpectedBranch) { throw 'BLOCK_WARP_BRANCH_MISMATCH' }
if ((Invoke-Git $Reality @('rev-parse','HEAD')) -ne $ExpectedRealityHead) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if ((Invoke-Git $Reality @('rev-parse','origin/master')) -ne $ExpectedRealityHead) { throw 'BLOCK_ORIGIN_MASTER_MISMATCH' }
if ((Invoke-Git $Reality @('status','--porcelain=v1'))) { throw 'BLOCK_REALITY_DIRTY' }
$statusLines = @((Invoke-Git $Repo @('status','--porcelain=v1') -split "`n") | Where-Object { $_ })
$unexpected = @($statusLines | Where-Object { $_ -notmatch '^\?\? WARP/PATCHES/IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002/' })
if ($unexpected.Count -gt 0) { throw "BLOCK_WARP_DIRTY_BEFORE_PATCH: $($unexpected -join '; ')" }
$LiveRoot = Join-Path $Repo "$CorridorReportRel/live_ui_evidence"
if (Test-Path -LiteralPath $LiveRoot) { throw 'BLOCK_PREEXISTING_LIVE_UI_EVIDENCE' }

$manifest = Get-Content -Raw (Join-Path $PatchRoot 'MANIFEST.json') | ConvertFrom-Json
foreach ($entry in $manifest.payload_files) {
    $source = Join-Path $PayloadRoot $entry.path
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "BLOCK_PAYLOAD_MISSING: $($entry.path)" }
    if ((Get-FileHash -Algorithm SHA256 $source).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "BLOCK_PAYLOAD_HASH: $($entry.path)" }
}
foreach ($entry in $manifest.preimages) {
    $target = Join-Path $Repo $entry.path
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "BLOCK_PREIMAGE_MISSING: $($entry.path)" }
    if ((Get-FileHash -Algorithm SHA256 $target).Hash.ToLowerInvariant() -ne $entry.sha256) { throw "BLOCK_PREIMAGE_HASH: $($entry.path)" }
}

New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
foreach ($entry in $manifest.preimages) {
    $source = Join-Path $Repo $entry.path
    $backup = Join-Path $BackupRoot $entry.path
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
    Copy-Item -LiteralPath $source -Destination $backup -Force
}
$RegistryPath = Join-Path $Repo "$CorridorReportRel/CAPABILITY_REGISTRY.json"
$RegistryBackup = Join-Path $BackupRoot "$CorridorReportRel/CAPABILITY_REGISTRY.json"
if (-not (Test-Path -LiteralPath $RegistryPath)) { throw 'BLOCK_CAPABILITY_REGISTRY_MISSING' }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $RegistryBackup) | Out-Null
Copy-Item -LiteralPath $RegistryPath -Destination $RegistryBackup -Force
foreach ($entry in $manifest.payload_files) {
    $source = Join-Path $PayloadRoot $entry.path
    $target = Join-Path $Repo $entry.path
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Force
}

try {
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $phase3 = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_tauri_surface.py -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) { $phase3 | Write-Host; throw 'BLOCK_PHASE3_ROUTE_REGRESSION' }
    $targeted = & python -B -m pytest `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_live_ui_evidence.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_ui_contract.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_real_diff.py `
        -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) { $targeted | Write-Host; throw 'BLOCK_TARGETED_TESTS' }
    $regression = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) { $regression | Write-Host; throw 'BLOCK_REGRESSION_TESTS' }
    Push-Location (Join-Path $Repo 'SUPPORT/APP_TAURI')
    try {
        & npm run build *> (Join-Path $PatchRoot 'npm_build.log')
        if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NPM_BUILD' }
    } finally { Pop-Location }
    & cargo check --manifest-path (Join-Path $Repo 'SUPPORT/APP_TAURI/src-tauri/Cargo.toml') *> (Join-Path $PatchRoot 'cargo_check.log')
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_CARGO_CHECK' }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $BaselinePath) | Out-Null
    $baselineOutput = & python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation `
        --mode baseline --repo $Repo --reality $Reality `
        --corridor-report (Join-Path $Repo $CorridorReportRel) --baseline $BaselinePath 2>&1
    if ($LASTEXITCODE -ne 0) { $baselineOutput | Write-Host; throw 'BLOCK_PHASE6_BASELINE' }
} catch {
    Restore-Payload $Repo $manifest
    Remove-Item (Join-Path $PatchRoot 'runtime') -Recurse -Force -ErrorAction SilentlyContinue
    throw
}

$phase3Count = ([regex]::Match(($phase3 -join "`n"), '(\d+) passed')).Groups[1].Value
$targetedCount = ([regex]::Match(($targeted -join "`n"), '(\d+) passed')).Groups[1].Value
$regressionCount = ([regex]::Match(($regression -join "`n"), '(\d+) passed')).Groups[1].Value
Write-Host "PATCH: $PatchId"
Write-Host "HEAD: $ExpectedHead"
Write-Host "TESTS: phase3=$phase3Count targeted=$targetedCount regression=$regressionCount"
Write-Host "BASELINE: $BaselinePath"
Write-Host 'ROOT_EVIDENCE_INDEX: SEALED_UNCHANGED_BASELINE'
Write-Host 'REALITY_UNCHANGED: True'
Write-Host 'NEXT_1: cd SUPPORT/APP_TAURI; npm run tauri:dev'
Write-Host 'NEXT_2: press Run Diagnostic exactly once, wait, press Refresh once, close app'
Write-Host "NEXT_3: pwsh WARP/PATCHES/$PatchId/VERIFY_$PatchId.ps1"
Write-Host 'VERDICT: LIVE_UI_BASELINE_CAPTURED_WAITING_FOR_OWNER_ACTION'
