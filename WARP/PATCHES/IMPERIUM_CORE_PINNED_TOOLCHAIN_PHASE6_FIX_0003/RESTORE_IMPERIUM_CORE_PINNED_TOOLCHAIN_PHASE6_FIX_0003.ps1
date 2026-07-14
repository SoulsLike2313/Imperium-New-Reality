$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$PatchId = 'IMPERIUM_CORE_PINNED_TOOLCHAIN_PHASE6_FIX_0003'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$Registry = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json'
$HardeningReport = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
if (-not (Test-Path $BackupRoot)) { throw 'BLOCK_BACKUP_MISSING' }
Get-ChildItem (Join-Path $BackupRoot 'files') -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    $relative = [IO.Path]::GetRelativePath((Join-Path $BackupRoot 'files'), $_.FullName)
    $destination = Join-Path $Root $relative
    New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
    Copy-Item $_.FullName $destination -Force
}
$newList = Join-Path $BackupRoot 'new_files.txt'
if (Test-Path $newList) {
    Get-Content $newList | Where-Object { $_ } | ForEach-Object { Remove-Item (Join-Path $Root $_) -Force -ErrorAction SilentlyContinue }
}
Copy-Item (Join-Path $BackupRoot 'CAPABILITY_REGISTRY.json') $Registry -Force
Remove-Item (Join-Path $HardeningReport 'PHASE6_LIVE_UI_BASELINE.json') -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $HardeningReport 'PINNED_TOOLCHAIN_RECEIPT.json') -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $HardeningReport 'LIVE_UI_ACTION_RECEIPT.json') -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $HardeningReport 'LIVE_UI_CORRIDOR_PROOF.md') -Force -ErrorAction SilentlyContinue
Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
Write-Host "PATCH: $PatchId"
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: RESTORED_TO_PHASE6_FIX2_STATE'
