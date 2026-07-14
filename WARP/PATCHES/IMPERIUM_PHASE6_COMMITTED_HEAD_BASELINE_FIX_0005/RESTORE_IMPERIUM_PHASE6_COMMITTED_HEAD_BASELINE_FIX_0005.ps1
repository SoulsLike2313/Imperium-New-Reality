$ErrorActionPreference = 'Stop'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchRoot = Join-Path $Root 'WARP/PATCHES/IMPERIUM_PHASE6_COMMITTED_HEAD_BASELINE_FIX_0005'
$Validator = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py'
$Test = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase6_committed_head_baseline.py'
$Backup = Join-Path $PatchRoot 'runtime_backup_phase6_live_ui_validation.py'
if (-not (Test-Path $Backup)) { throw 'BLOCK_BACKUP_MISSING' }
Copy-Item $Backup $Validator -Force
Remove-Item $Test -Force -ErrorAction SilentlyContinue
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: COMMITTED_HEAD_BASELINE_SUPPORT_RESTORED'
