$ErrorActionPreference = 'Stop'
$PatchId = 'IMPERIUM_PHASE2_WINDOWS_PROCESS_PROBE_HARDENING_0001'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$Receipt = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/PHASE2_WINDOWS_PROCESS_PROBE_RECEIPT.json'
if (-not (Test-Path $BackupRoot)) { throw 'BLOCK_NO_RUNTIME_BACKUP' }
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
Remove-Item $Receipt -Force -ErrorAction SilentlyContinue
Write-Host "PATCH: $PatchId"
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: RESTORED_PROCESS_PROBE_HARDENING'
