$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ExpectedHead = 'f686b90ea0d2e1af06e2243dd543324f5be6c9e3'
$PatchRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$Repo = (& git -C (Get-Location).Path rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NOT_GIT_REPO' }
if ((& git -C $Repo rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_RESTORE_AFTER_COMMIT: restore is only allowed before Phase 5 commit' }
if (-not (Test-Path $BackupRoot)) { throw 'BLOCK_BACKUP_MISSING' }
$manifest = Get-Content -Raw (Join-Path $PatchRoot 'MANIFEST.json') | ConvertFrom-Json
foreach ($entry in $manifest.preimages) {
    $backup = Join-Path $BackupRoot $entry.path
    $target = Join-Path $Repo $entry.path
    Copy-Item -LiteralPath $backup -Destination $target -Force
}
foreach ($entry in $manifest.added_files) {
    $target = Join-Path $Repo $entry
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
}
foreach ($name in @('REAL_DIFF_RECEIPT.json','REAL_DIFF_PROOF.md')) {
    $target = Join-Path $Repo 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
    $target = Join-Path $target $name
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
}
Write-Host 'PATCH: IMPERIUM_CORE_REAL_DIFF_0001'
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: RESTORED_TO_PRE_PHASE5_WORKTREE'
