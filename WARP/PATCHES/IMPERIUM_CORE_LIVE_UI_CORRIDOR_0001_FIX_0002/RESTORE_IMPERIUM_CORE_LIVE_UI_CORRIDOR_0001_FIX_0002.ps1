$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$PatchId = 'IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002'
$ExpectedHead = '8f34f78f6dc36b82989ac51e2e2baedba26872de'
$PatchRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$Repo = (& git -C (Get-Location).Path rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NOT_GIT_REPO' }
if ((& git -C $Repo rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_RESTORE_AFTER_COMMIT' }
if (-not (Test-Path -LiteralPath $BackupRoot)) { throw 'BLOCK_BACKUP_MISSING' }
$manifest = Get-Content -Raw (Join-Path $PatchRoot 'MANIFEST.json') | ConvertFrom-Json
foreach ($entry in $manifest.preimages) {
    $backup = Join-Path $BackupRoot $entry.path
    $target = Join-Path $Repo $entry.path
    if (-not (Test-Path -LiteralPath $backup)) { throw "BLOCK_BACKUP_FILE_MISSING: $($entry.path)" }
    Copy-Item -LiteralPath $backup -Destination $target -Force
}
foreach ($entry in $manifest.added_files) {
    $target = Join-Path $Repo $entry
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
}
$CorridorReportRel = 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$RegistryBackup = Join-Path $BackupRoot "$CorridorReportRel/CAPABILITY_REGISTRY.json"
$RegistryTarget = Join-Path $Repo "$CorridorReportRel/CAPABILITY_REGISTRY.json"
if (Test-Path -LiteralPath $RegistryBackup) { Copy-Item -LiteralPath $RegistryBackup -Destination $RegistryTarget -Force }
$LiveRoot = Join-Path $Repo "$CorridorReportRel/live_ui_evidence"
if (Test-Path -LiteralPath $LiveRoot) { Remove-Item -LiteralPath $LiveRoot -Recurse -Force }
$Hardening = Join-Path $Repo 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
foreach ($name in @('LIVE_UI_ACTION_RECEIPT.json','LIVE_UI_CORRIDOR_PROOF.md')) {
    $target = Join-Path $Hardening $name
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
}
Remove-Item (Join-Path $PatchRoot 'runtime') -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "PATCH: $PatchId"
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: RESTORED_TO_PRE_PHASE6_WORKTREE'
