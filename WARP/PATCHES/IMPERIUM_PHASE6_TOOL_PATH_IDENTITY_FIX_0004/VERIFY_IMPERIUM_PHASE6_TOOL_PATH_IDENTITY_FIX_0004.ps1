$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = (git rev-parse --show-toplevel).Trim()
$Receipt = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/LIVE_UI_ACTION_RECEIPT.json'
$Proof = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/LIVE_UI_CORRIDOR_PROOF.md'
if (-not (Test-Path $Receipt)) { throw 'BLOCK_RECEIPT_MISSING' }
if (-not (Test-Path $Proof)) { throw 'BLOCK_PROOF_MISSING' }
$Value = Get-Content -Raw $Receipt | ConvertFrom-Json
if ($Value.verdict -ne 'LIVE_UI_CORRIDOR_PROVEN') { throw 'BLOCK_VERDICT' }
Write-Host "ACTION_REQUEST: $($Value.action_request_id)"
Write-Host "EVIDENCE: $($Value.evidence_id)"
Write-Host "LIVE_COUNT: $($Value.live_count_before) -> $($Value.live_count_after)"
Write-Host "TOOL_PATH_IDENTITY: $($Value.tool_path_identity_rule)"
Write-Host "PATH_RESOLUTION_USED: $($Value.path_resolution_used)"
Write-Host "PHASE3_SURFACE: $($Value.phase3_surface_verdict)"
Write-Host "REALITY_UNCHANGED: $($Value.reality_unchanged)"
Write-Host 'VERDICT: LIVE_UI_CORRIDOR_PROVEN'
