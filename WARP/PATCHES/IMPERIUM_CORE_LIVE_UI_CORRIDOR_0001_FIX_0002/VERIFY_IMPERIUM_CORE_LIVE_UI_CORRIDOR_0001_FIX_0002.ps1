$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$PatchId = 'IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002'
$ExpectedHead = '8f34f78f6dc36b82989ac51e2e2baedba26872de'
$ExpectedRealityHead = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$PatchRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PayloadRoot = Join-Path $PatchRoot 'payload'
$BaselinePath = Join-Path $PatchRoot 'runtime/LIVE_UI_BASELINE.json'
$Repo = (& git -C (Get-Location).Path rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NOT_GIT_REPO' }
$Reality = 'E:\IMPERIUM_REALITY'
if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
if ((& git -C $Repo rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
if ((& git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedRealityHead) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if ((& git -C $Reality status --porcelain=v1)) { throw 'BLOCK_REALITY_DIRTY' }
if (-not (Test-Path -LiteralPath $BaselinePath)) { throw 'BLOCK_BASELINE_MISSING' }
$manifest = Get-Content -Raw (Join-Path $PatchRoot 'MANIFEST.json') | ConvertFrom-Json
foreach ($entry in $manifest.payload_files) {
    $source = Join-Path $PayloadRoot $entry.path
    $target = Join-Path $Repo $entry.path
    $expected = (Get-FileHash -Algorithm SHA256 $source).Hash.ToLowerInvariant()
    if (-not (Test-Path -LiteralPath $target) -or (Get-FileHash -Algorithm SHA256 $target).Hash.ToLowerInvariant() -ne $expected) { throw "BLOCK_IMPLEMENTATION_DRIFT: $($entry.path)" }
}
$env:PYTHONDONTWRITEBYTECODE = '1'
$phase3 = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_tauri_surface.py -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $phase3 | Write-Host; throw 'BLOCK_PHASE3_ROUTE_REGRESSION' }
$HardeningReport = Join-Path $Repo 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
New-Item -ItemType Directory -Force -Path $HardeningReport | Out-Null
$output = & python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation `
    --mode verify --repo $Repo --reality $Reality `
    --corridor-report (Join-Path $Repo 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001') `
    --baseline $BaselinePath --hardening-report $HardeningReport 2>&1
if ($LASTEXITCODE -ne 0) { $output | Write-Host; throw 'BLOCK_PHASE6_LIVE_UI_VALIDATION' }
$targeted = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_live_ui_evidence.py ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_ui_contract.py ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_real_diff.py -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $targeted | Write-Host; throw 'BLOCK_TARGETED_TESTS' }
$regression = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $regression | Write-Host; throw 'BLOCK_REGRESSION_TESTS' }
$receiptPath = Join-Path $HardeningReport 'LIVE_UI_ACTION_RECEIPT.json'
$receipt = Get-Content -Raw $receiptPath | ConvertFrom-Json
if ($receipt.verdict -ne 'LIVE_UI_CORRIDOR_PROVEN') { throw "BLOCK_PHASE6_VERDICT: $($receipt.verdict)" }
Write-Host "PATCH: $PatchId"
Write-Host "ACTION_REQUEST: $($receipt.action_request_id)"
Write-Host "EVIDENCE: $($receipt.evidence_id)"
Write-Host "LIVE_COUNT: $($receipt.live_count_before) -> $($receipt.live_count_after)"
Write-Host "SNAPSHOT_COUNT: $($receipt.snapshot_live_count)"
Write-Host "ROOT_INDEX_UNCHANGED: $($receipt.root_index_unchanged)"
Write-Host "PHASE3_SURFACE: $($receipt.phase3_surface_verdict)"
Write-Host "REALITY_UNCHANGED: $($receipt.reality_unchanged)"
Write-Host "RECEIPT: $receiptPath"
Write-Host "VERDICT: $($receipt.verdict)"
