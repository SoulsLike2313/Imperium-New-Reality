$ErrorActionPreference = 'Stop'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchId = 'IMPERIUM_PHASE7_CLAIM_RECONCILIATION_0001'
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Backup = Join-Path $PatchRoot 'runtime_backup'
$Files = @(
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/ui_snapshot.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase7_claim_reconciliation.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase7_disk_auditor.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_claim_reconciliation.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_ui_truth.py',
    'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/KNOWN_GAPS.md',
    'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/KNOWN_GAPS.md'
)
foreach ($Relative in $Files) {
    $Target = Join-Path $Root $Relative
    $Saved = Join-Path $Backup $Relative
    if (Test-Path $Saved) {
        New-Item -ItemType Directory -Path (Split-Path $Target) -Force | Out-Null
        Copy-Item $Saved $Target -Force
    }
    else {
        Remove-Item $Target -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "PATCH: $PatchId"
Write-Host 'RESTORE: COMPLETED'
Write-Host 'VERDICT: PHASE7_IMPLEMENTATION_RESTORED'
