$ErrorActionPreference = 'Stop'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchId = 'IMPERIUM_PHASE6_TOOL_PATH_IDENTITY_FIX_0004'
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Validator = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py'
$Test = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase6_tool_path_identity.py'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Backup = Join-Path $PatchRoot 'runtime_backup_phase6_live_ui_validation.py'
if (-not (Test-Path $Backup)) { throw 'BLOCK_BACKUP_MISSING' }
Copy-Item $Backup $Validator -Force
Remove-Item $Test -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $Hardening 'LIVE_UI_ACTION_RECEIPT.json') -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $Hardening 'LIVE_UI_CORRIDOR_PROOF.md') -Force -ErrorAction SilentlyContinue
Write-Host "PATCH: $PatchId"
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: PHASE6_PATH_IDENTITY_FIX_RESTORED'
