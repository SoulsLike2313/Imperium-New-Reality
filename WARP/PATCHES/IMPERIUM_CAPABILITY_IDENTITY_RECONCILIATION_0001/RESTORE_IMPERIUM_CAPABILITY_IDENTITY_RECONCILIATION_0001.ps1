$ErrorActionPreference = 'Stop'
$PatchId = 'IMPERIUM_CAPABILITY_IDENTITY_RECONCILIATION_0001'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Registry = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json'
$Receipt = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/CAPABILITY_IDENTITY_RECONCILIATION_RECEIPT.json'
$Backup = Join-Path $PatchRoot 'runtime_backup_CAPABILITY_REGISTRY.json'
if (-not (Test-Path $Backup)) { throw 'BLOCK_BACKUP_MISSING' }
Copy-Item $Backup $Registry -Force
Remove-Item $Receipt -Force -ErrorAction SilentlyContinue
Write-Host "PATCH: $PatchId"
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: REGISTRY_RESTORED'
