$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_PHASE7_CLAIM_RECONCILIATION_0001'
$BaseImplementation = 'dc3079e4ac9e299761317d6bc078ce1ac3f18c8d'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$Root = (git rev-parse --show-toplevel).Trim()
$Reality = 'E:\IMPERIUM_REALITY'
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Report = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Head = (git rev-parse HEAD).Trim()

if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
if ((git branch --show-current).Trim() -ne $ExpectedBranch) { throw 'BLOCK_BRANCH_MISMATCH' }
if ($Head -eq $BaseImplementation) { throw 'BLOCK_PHASE7_IMPLEMENTATION_NOT_COMMITTED' }
git merge-base --is-ancestor $BaseImplementation $Head
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE7_HEAD_NOT_DESCENDANT' }
if (git status --porcelain=v1 --untracked-files=no) { throw 'BLOCK_TRACKED_WORKTREE_DIRTY' }
if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }

foreach ($Required in @(
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase7_claim_reconciliation.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase7_disk_auditor.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_claim_reconciliation.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_ui_truth.py'
)) {
    git cat-file -e "$($Head):$Required"
    if ($LASTEXITCODE -ne 0) { throw "BLOCK_PHASE7_COMMITTED_FILE_MISSING: $Required" }
}

$ToolReceipt = Get-Content -Raw (Join-Path $Hardening 'PINNED_TOOLCHAIN_RECEIPT.json') | ConvertFrom-Json
$env:IMPERIUM_PINNED_TOOLCHAIN_REQUIRED = '1'
$env:IMPERIUM_GIT_EXECUTABLE = $ToolReceipt.git.executable
$env:IMPERIUM_GIT_SHA256 = $ToolReceipt.git.sha256
$env:IMPERIUM_PWSH_EXECUTABLE = $ToolReceipt.pwsh.executable
$env:IMPERIUM_PWSH_SHA256 = $ToolReceipt.pwsh.sha256
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUTF8 = '1'

$Python = (Get-Command python.exe -ErrorAction Stop).Source
$TargetedXml = Join-Path $Hardening 'PHASE_7_TEST_RESULTS.xml'
$RegressionXml = Join-Path $Hardening 'PHASE_7_REGRESSION_RESULTS.xml'

& $Python -B -m pytest `
    (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_claim_reconciliation.py') `
    (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_ui_truth.py') `
    (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_ui_contract.py') `
    -q -p no:cacheprovider --junitxml $TargetedXml
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE7_TARGETED_TESTS' }

& $Python -B -m pytest `
    (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests') `
    -q -p no:cacheprovider --junitxml $RegressionXml
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE7_REGRESSION' }

cargo test --manifest-path (Join-Path $Root 'SUPPORT/APP_TAURI/src-tauri/Cargo.toml') --no-default-features
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_RUST_TESTS' }
cargo check --manifest-path (Join-Path $Root 'SUPPORT/APP_TAURI/src-tauri/Cargo.toml') --no-default-features
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_CARGO_CHECK' }
Push-Location (Join-Path $Root 'SUPPORT/APP_TAURI')
try {
    npm run build
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NPM_BUILD' }
}
finally {
    Pop-Location
}

& $Python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase7_claim_reconciliation `
    --repo $Root `
    --reality $Reality `
    --corridor-report $Report `
    --hardening-report $Hardening `
    --output-root $Report `
    --mode final
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_FINAL_RECONCILIATION' }

# Move the Phase 7 receipt copies to the hardening authority while preserving
# the report-root current claim artifacts used by the Thin IDE.
Copy-Item (Join-Path $Report 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.json') (Join-Path $Hardening 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.json') -Force
Copy-Item (Join-Path $Report 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.md') (Join-Path $Hardening 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.md') -Force
Remove-Item (Join-Path $Report 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.json') -Force
Remove-Item (Join-Path $Report 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.md') -Force

& $Python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase7_disk_auditor `
    --repo $Root `
    --reality $Reality `
    --corridor-report $Report `
    --hardening-report $Hardening `
    --claim-status (Join-Path $Report 'CURRENT_CLAIM_STATUS.json') `
    --output (Join-Path $Hardening 'PHASE7_INDEPENDENT_DISK_AUDIT.json') `
    --mode final
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_FINAL_DISK_AUDIT' }

$Claim = Get-Content -Raw (Join-Path $Hardening 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.json') | ConvertFrom-Json
$Audit = Get-Content -Raw (Join-Path $Hardening 'PHASE7_INDEPENDENT_DISK_AUDIT.json') | ConvertFrom-Json
if ($Claim.verdict -ne 'REFERENCE_CORRIDOR_PASS_WITH_DEBT') { throw "BLOCK_FINAL_CLAIM_VERDICT: $($Claim.verdict)" }
if ($Audit.verdict -ne $Claim.verdict) { throw 'BLOCK_AUDITOR_DISAGREES' }
if ($Claim.implementation_head -ne $Head -or $Audit.implementation_head -ne $Head) { throw 'BLOCK_HEAD_BINDING' }
if (-not $Audit.reality_unchanged) { throw 'BLOCK_REALITY_CHANGED' }

Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
Write-Host "PATCH: $PatchId"
Write-Host "IMPLEMENTATION_HEAD: $Head"
Write-Host "CLAIM_RECONCILIATION: $($Claim.verdict)"
Write-Host "INDEPENDENT_DISK_AUDIT: $($Audit.verdict)"
Write-Host "MUTATION_TESTS: $($Audit.mutation_tests.count) detected"
Write-Host "CURRENT_ORGAN_RING: $($Claim.organ_ring_current_verdict)"
Write-Host "HISTORICAL_ORGAN_PASS_PROMOTED: $($Claim.historical_organ_rows_promoted)"
Write-Host "UI_ORGAN_PANEL: $($Audit.ui_organ_panel_status)"
Write-Host "DEBTS: $($Claim.debt_count)"
Write-Host "REALITY_UNCHANGED: $($Audit.reality_unchanged)"
Write-Host 'LAND_AUTHORIZED: False'
Write-Host "CLAIM_RECEIPT: $(Join-Path $Hardening 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.json')"
Write-Host "AUDIT_RECEIPT: $(Join-Path $Hardening 'PHASE7_INDEPENDENT_DISK_AUDIT.json')"
Write-Host 'VERDICT: REFERENCE_CORRIDOR_PASS_WITH_DEBT'
