$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Root = (git rev-parse --show-toplevel).Trim()
$Reality = 'E:\IMPERIUM_REALITY'
$Report = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Baseline = Join-Path $Hardening 'PHASE6_LIVE_UI_BASELINE.json'
$OldReceipt = Join-Path $Hardening 'LIVE_UI_ACTION_RECEIPT.json'
$OldProof = Join-Path $Hardening 'LIVE_UI_CORRIDOR_PROOF.md'
$Archive = Join-Path $Hardening 'PHASE6_ATTEMPT_01_PRECOMMIT'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'

if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
if (git status --porcelain=v1 --untracked-files=no) { throw 'BLOCK_TRACKED_WORKTREE_DIRTY' }
if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }

$Source = Get-Content -Raw (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py')
if ($Source -notmatch 'imperium\.phase6_live_ui_baseline\.v3') {
    throw 'BLOCK_COMMITTED_HEAD_BASELINE_SUPPORT_MISSING'
}

New-Item -ItemType Directory -Path $Archive -Force | Out-Null
foreach ($Path in @($Baseline, $OldReceipt, $OldProof)) {
    if (Test-Path $Path) {
        Copy-Item $Path (Join-Path $Archive (Split-Path $Path -Leaf)) -Force
    }
}

$OldBaselineValue = if (Test-Path $Baseline) { Get-Content -Raw $Baseline | ConvertFrom-Json } else { $null }
$OldReceiptValue = if (Test-Path $OldReceipt) { Get-Content -Raw $OldReceipt | ConvertFrom-Json } else { $null }

[ordered]@{
    schema_version = 'imperium.phase6_historical_attempt.v1'
    verdict = 'HISTORICAL_PRECOMMIT_ATTEMPT_NOT_FINAL'
    reason = 'Implementation HEAD changed after the first baseline; no retroactive rebinding is allowed.'
    baseline_implementation_head = $OldBaselineValue.implementation_head
    action_request_id = $OldReceiptValue.action_request_id
    evidence_id = $OldReceiptValue.evidence_id
    preserved_live_evidence = $true
} | ConvertTo-Json -Depth 6 |
    Set-Content (Join-Path $Archive 'ATTEMPT_01_STATUS.json') -Encoding utf8

Remove-Item $Baseline -Force -ErrorAction SilentlyContinue
Remove-Item $OldReceipt -Force -ErrorAction SilentlyContinue
Remove-Item $OldProof -Force -ErrorAction SilentlyContinue

$Python = (Get-Command python.exe -ErrorAction Stop).Source
& $Python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation `
    --mode baseline `
    --repo $Root `
    --reality $Reality `
    --corridor-report $Report `
    --baseline $Baseline
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NEW_BASELINE_CAPTURE' }

$Value = Get-Content -Raw $Baseline | ConvertFrom-Json
$Head = (git rev-parse HEAD).Trim()
if ($Value.schema_version -ne 'imperium.phase6_live_ui_baseline.v3') { throw 'BLOCK_BASELINE_SCHEMA' }
if ($Value.implementation_head -ne $Head) { throw 'BLOCK_BASELINE_HEAD_BINDING' }
if ($Value.implementation_tracked_status.Count -ne 0) { throw 'BLOCK_BASELINE_TRACKED_DIRTY' }
if ($Value.live_evidence_ids.Count -ne 1) { throw "BLOCK_EXPECTED_ONE_HISTORICAL_EVIDENCE: $($Value.live_evidence_ids.Count)" }

Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
Write-Host "IMPLEMENTATION_HEAD: $Head"
Write-Host "HISTORICAL_LIVE_COUNT: $($Value.live_evidence_ids.Count)"
Write-Host "ARCHIVE: $Archive"
Write-Host "BASELINE: $Baseline"
Write-Host 'OWNER_ACTION_REQUIRED: Run Diagnostic once, wait, Refresh once, close app'
Write-Host 'VERDICT: LIVE_UI_BASELINE_CAPTURED_ON_COMMITTED_HEAD'
