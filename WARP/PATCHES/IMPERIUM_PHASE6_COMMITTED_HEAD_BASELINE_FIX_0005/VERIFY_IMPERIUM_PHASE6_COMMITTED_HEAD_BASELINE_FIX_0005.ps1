$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Root = (git rev-parse --show-toplevel).Trim()
$Reality = 'E:\IMPERIUM_REALITY'
$Report = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Baseline = Join-Path $Hardening 'PHASE6_LIVE_UI_BASELINE.json'
$Receipt = Join-Path $Hardening 'LIVE_UI_ACTION_RECEIPT.json'
$Proof = Join-Path $Hardening 'LIVE_UI_CORRIDOR_PROOF.md'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'

if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
if (git status --porcelain=v1 --untracked-files=no) { throw 'BLOCK_TRACKED_WORKTREE_DIRTY_AFTER_BASELINE' }
if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }

$Python = (Get-Command python.exe -ErrorAction Stop).Source
& $Python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation `
    --mode verify `
    --repo $Root `
    --reality $Reality `
    --corridor-report $Report `
    --baseline $Baseline `
    --hardening-report $Hardening
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE6_VERIFY' }

$Value = Get-Content -Raw $Receipt | ConvertFrom-Json
$Head = (git rev-parse HEAD).Trim()
if ($Value.verdict -ne 'LIVE_UI_CORRIDOR_PROVEN') { throw 'BLOCK_VERDICT' }
if ($Value.implementation_head -ne $Head) { throw 'BLOCK_RECEIPT_HEAD_BINDING' }
if ($Value.live_count_before -ne 1 -or $Value.live_count_after -ne 2) {
    throw "BLOCK_LIVE_COUNT: $($Value.live_count_before) -> $($Value.live_count_after)"
}
if ($Value.path_resolution_used -ne $false) { throw 'BLOCK_PATH_RESOLUTION' }
if ($Value.phase3_surface_verdict -ne 'LEGACY_MUTATION_SURFACE_CLOSED') { throw 'BLOCK_PHASE3' }
if (-not $Value.reality_unchanged) { throw 'BLOCK_REALITY_CHANGED' }
if (-not (Test-Path $Proof)) { throw 'BLOCK_PROOF_MISSING' }

Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
Write-Host "IMPLEMENTATION_HEAD: $($Value.implementation_head)"
Write-Host "ACTION_REQUEST: $($Value.action_request_id)"
Write-Host "EVIDENCE: $($Value.evidence_id)"
Write-Host "LIVE_COUNT: $($Value.live_count_before) -> $($Value.live_count_after)"
Write-Host "PATH_RESOLUTION_USED: $($Value.path_resolution_used)"
Write-Host "PHASE3_SURFACE: $($Value.phase3_surface_verdict)"
Write-Host "REALITY_UNCHANGED: $($Value.reality_unchanged)"
Write-Host "RECEIPT: $Receipt"
Write-Host 'VERDICT: LIVE_UI_CORRIDOR_PROVEN_ON_COMMITTED_HEAD'
