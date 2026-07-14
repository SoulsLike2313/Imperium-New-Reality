$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_PHASE6_REGISTRY_RUNTIME_TRANSITION_PROOF_0006'
$ExpectedHead = '5da51c51199f759d4dbe04d15249f137f56dc27c'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$RegistryRel = 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json'
$Root = (git rev-parse --show-toplevel).Trim()
$Reality = 'E:\IMPERIUM_REALITY'
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Registry = Join-Path $Root $RegistryRel
$Report = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Baseline = Join-Path $Hardening 'PHASE6_LIVE_UI_BASELINE.json'
$LiveIndex = Join-Path $Report 'live_ui_evidence/EVIDENCE_INDEX.json'
$TransitionReceipt = Join-Path $Hardening 'PHASE6_REGISTRY_RUNTIME_TRANSITION_RECEIPT.json'
$ActionReceipt = Join-Path $Hardening 'LIVE_UI_ACTION_RECEIPT.json'
$Proof = Join-Path $Hardening 'LIVE_UI_CORRIDOR_PROOF.md'

if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
$Head = (git rev-parse HEAD).Trim()
if ($Head -ne $ExpectedHead) { throw "BLOCK_WARP_HEAD_MISMATCH: $Head" }
if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }

$Tracked = @(git diff --name-only)
if ($Tracked.Count -ne 1 -or $Tracked[0] -ne $RegistryRel) {
    $Tracked | Write-Host
    throw 'BLOCK_UNEXPECTED_TRACKED_MUTATION'
}

foreach ($Required in @($Registry, $Baseline, $LiveIndex)) {
    if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) {
        throw "BLOCK_REQUIRED_FILE_MISSING: $Required"
    }
}

$Python = (Get-Command python.exe -ErrorAction Stop).Source

& $Python -B (Join-Path $PatchRoot 'tools/verify_registry_transition.py') --self-test
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_TRANSITION_SELF_TEST' }

& $Python -B (Join-Path $PatchRoot 'tools/verify_registry_transition.py') `
    --repo $Root `
    --head $Head `
    --registry $Registry `
    --baseline $Baseline `
    --live-index $LiveIndex `
    --receipt $TransitionReceipt
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_REGISTRY_TRANSITION_PROOF' }

& $Python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation `
    --mode verify `
    --repo $Root `
    --reality $Reality `
    --corridor-report $Report `
    --baseline $Baseline `
    --hardening-report $Hardening
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE6_COMMITTED_VERIFIER' }

$Transition = Get-Content -Raw $TransitionReceipt | ConvertFrom-Json
$Action = Get-Content -Raw $ActionReceipt | ConvertFrom-Json

if ($Transition.verdict -ne 'EXACT_RUNTIME_REGISTRY_TRANSITION_PROVEN') {
    throw 'BLOCK_TRANSITION_RECEIPT_VERDICT'
}
if ($Action.verdict -ne 'LIVE_UI_CORRIDOR_PROVEN') { throw 'BLOCK_ACTION_VERDICT' }
if ($Action.implementation_head -ne $Head) { throw 'BLOCK_ACTION_HEAD_BINDING' }
if ($Action.evidence_id -ne $Transition.new_evidence_id) {
    throw 'BLOCK_ACTION_TRANSITION_EVIDENCE_MISMATCH'
}
if ($Action.live_count_before -ne 1 -or $Action.live_count_after -ne 2) {
    throw "BLOCK_LIVE_COUNT: $($Action.live_count_before) -> $($Action.live_count_after)"
}
if ($Action.path_resolution_used -ne $false) { throw 'BLOCK_PATH_RESOLUTION' }
if ($Action.phase3_surface_verdict -ne 'LEGACY_MUTATION_SURFACE_CLOSED') { throw 'BLOCK_PHASE3' }
if (-not $Action.reality_unchanged) { throw 'BLOCK_REALITY_CHANGED' }
if (-not (Test-Path $Proof)) { throw 'BLOCK_PROOF_MISSING' }

Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
Write-Host "PATCH: $PatchId"
Write-Host "IMPLEMENTATION_HEAD: $Head"
Write-Host "TRACKED_RUNTIME_MUTATION: $RegistryRel"
Write-Host 'ALL_OTHER_TRACKED_FILES_UNCHANGED: True'
Write-Host "HISTORICAL_EVIDENCE: $($Transition.historical_evidence_id)"
Write-Host "NEW_EVIDENCE: $($Transition.new_evidence_id)"
Write-Host "LIVE_COUNT: $($Action.live_count_before) -> $($Action.live_count_after)"
Write-Host 'REGISTRY_TRANSITION: EXACT_CORE_DIAGNOSTIC_LAST_VALIDATION_ONLY'
Write-Host "REGISTRY_DIGEST: $($Transition.registry_digest_before) -> $($Transition.registry_digest_after)"
Write-Host "PATH_RESOLUTION_USED: $($Action.path_resolution_used)"
Write-Host "PHASE3_SURFACE: $($Action.phase3_surface_verdict)"
Write-Host "REALITY_UNCHANGED: $($Action.reality_unchanged)"
Write-Host "TRANSITION_RECEIPT: $TransitionReceipt"
Write-Host "ACTION_RECEIPT: $ActionReceipt"
Write-Host 'VERDICT: LIVE_UI_CORRIDOR_PROVEN_ON_COMMITTED_HEAD'
