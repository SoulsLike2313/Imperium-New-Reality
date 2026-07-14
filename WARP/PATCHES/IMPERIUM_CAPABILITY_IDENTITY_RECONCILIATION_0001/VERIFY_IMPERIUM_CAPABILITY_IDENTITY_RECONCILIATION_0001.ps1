$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = (git rev-parse --show-toplevel).Trim()
$Registry = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json'
$Receipt = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/CAPABILITY_IDENTITY_RECONCILIATION_RECEIPT.json'
if (-not (Test-Path $Receipt)) { throw 'BLOCK_RECEIPT_MISSING' }
$Value = Get-Content -Raw $Receipt | ConvertFrom-Json
if ($Value.verdict -ne 'CAPABILITY_IDENTITY_RECONCILED') { throw 'BLOCK_RECEIPT_VERDICT' }
if ($Value.remaining_mismatches.Count -ne 0) { throw 'BLOCK_MISMATCHES_REMAIN' }
Write-Host "REGISTRY: $Registry"
Write-Host "RECONCILED: $($Value.changes.capability_id -join ', ')"
Write-Host "REGISTRY_DIGEST: $($Value.registry_digest_after)"
Write-Host 'VERDICT: CAPABILITY_IDENTITY_RECONCILED'
