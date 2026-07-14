$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = (git rev-parse --show-toplevel).Trim()
$Report = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Claim = Get-Content -Raw (Join-Path $Hardening 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.json') | ConvertFrom-Json
$Audit = Get-Content -Raw (Join-Path $Hardening 'PHASE7_INDEPENDENT_DISK_AUDIT.json') | ConvertFrom-Json
$Status = Get-Content -Raw (Join-Path $Report 'CURRENT_CLAIM_STATUS.json') | ConvertFrom-Json
if ($Claim.verdict -ne 'REFERENCE_CORRIDOR_PASS_WITH_DEBT') { throw 'BLOCK_CLAIM' }
if ($Audit.verdict -ne $Claim.verdict) { throw 'BLOCK_AUDIT' }
if ($Status.campaign_verdict -ne $Claim.verdict) { throw 'BLOCK_STATUS' }
if ($Status.organ_ring_verdict -ne 'NOT_PROVEN') { throw 'BLOCK_ORGAN_OVERCLAIM' }
if (-not $Audit.reality_unchanged) { throw 'BLOCK_REALITY' }
Write-Host "IMPLEMENTATION_HEAD: $($Claim.implementation_head)"
Write-Host "CLAIM_RECONCILIATION: $($Claim.verdict)"
Write-Host "INDEPENDENT_DISK_AUDIT: $($Audit.verdict)"
Write-Host "MUTATION_TESTS: $($Audit.mutation_tests.count)"
Write-Host "CURRENT_ORGAN_RING: $($Status.organ_ring_verdict)"
Write-Host "DEBTS: $($Claim.debt_count)"
Write-Host "REALITY_UNCHANGED: $($Audit.reality_unchanged)"
Write-Host 'LAND_AUTHORIZED: False'
Write-Host 'VERDICT: REFERENCE_CORRIDOR_PASS_WITH_DEBT'
