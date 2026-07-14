$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = (git rev-parse --show-toplevel).Trim()
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$TransitionPath = Join-Path $Hardening 'PHASE6_REGISTRY_RUNTIME_TRANSITION_RECEIPT.json'
$ActionPath = Join-Path $Hardening 'LIVE_UI_ACTION_RECEIPT.json'
foreach ($Path in @($TransitionPath, $ActionPath)) {
    if (-not (Test-Path $Path)) { throw "BLOCK_RECEIPT_MISSING: $Path" }
}
$Transition = Get-Content -Raw $TransitionPath | ConvertFrom-Json
$Action = Get-Content -Raw $ActionPath | ConvertFrom-Json
if ($Transition.verdict -ne 'EXACT_RUNTIME_REGISTRY_TRANSITION_PROVEN') { throw 'BLOCK_TRANSITION' }
if ($Action.verdict -ne 'LIVE_UI_CORRIDOR_PROVEN') { throw 'BLOCK_ACTION' }
if ($Transition.new_evidence_id -ne $Action.evidence_id) { throw 'BLOCK_EVIDENCE_LINK' }
Write-Host "IMPLEMENTATION_HEAD: $($Action.implementation_head)"
Write-Host "EVIDENCE: $($Action.evidence_id)"
Write-Host "LIVE_COUNT: $($Action.live_count_before) -> $($Action.live_count_after)"
Write-Host 'REGISTRY_TRANSITION: EXACT_CORE_DIAGNOSTIC_LAST_VALIDATION_ONLY'
Write-Host "PATH_RESOLUTION_USED: $($Action.path_resolution_used)"
Write-Host "PHASE3_SURFACE: $($Action.phase3_surface_verdict)"
Write-Host "REALITY_UNCHANGED: $($Action.reality_unchanged)"
Write-Host 'VERDICT: LIVE_UI_CORRIDOR_PROVEN_ON_COMMITTED_HEAD'
