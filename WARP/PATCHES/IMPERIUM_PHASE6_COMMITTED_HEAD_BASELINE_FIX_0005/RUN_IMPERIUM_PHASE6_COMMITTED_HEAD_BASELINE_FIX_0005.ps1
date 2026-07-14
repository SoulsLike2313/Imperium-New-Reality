$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_PHASE6_COMMITTED_HEAD_BASELINE_FIX_0005'
$ExpectedHead = '8c3a3630478c53e19fead8e18ec165adc5062cbe'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$ExpectedValidatorSha = '8ec4a28d0d8af15589753243b573020cfe7db84b2924d8fd8dee247759cc978d'
$Root = (git rev-parse --show-toplevel).Trim()
$Validator = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py'
$Test = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase6_committed_head_baseline.py'
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Reality = 'E:\IMPERIUM_REALITY'
$Backup = Join-Path $PatchRoot 'runtime_backup_phase6_live_ui_validation.py'

function Restore-Local {
    if (Test-Path $Backup) { Copy-Item $Backup $Validator -Force }
    Remove-Item $Test -Force -ErrorAction SilentlyContinue
}

try {
    if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
    if ((git rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
    if ((git branch --show-current).Trim() -ne $ExpectedBranch) { throw 'BLOCK_BRANCH_MISMATCH' }
    if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }
    if (git status --porcelain=v1 --untracked-files=no) { throw 'BLOCK_TRACKED_WORKTREE_DIRTY' }

    $ActualValidatorSha = (Get-FileHash $Validator -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ActualValidatorSha -ne $ExpectedValidatorSha) {
        throw "BLOCK_VALIDATOR_SOURCE_DRIFT: $ActualValidatorSha"
    }

    Copy-Item $Validator $Backup -Force
    Copy-Item (Join-Path $PatchRoot 'payload/ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py') $Validator -Force
    New-Item -ItemType Directory -Path (Split-Path $Test) -Force | Out-Null
    Copy-Item (Join-Path $PatchRoot 'payload/ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase6_committed_head_baseline.py') $Test -Force

    $Python = (Get-Command python.exe -ErrorAction Stop).Source

    $Targeted = & $Python -B -m pytest `
        $Test `
        (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_live_ui_evidence.py') `
        (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase6_tool_path_identity.py') `
        -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) {
        $Targeted | Write-Host
        throw 'BLOCK_TARGETED_TESTS'
    }

    $Regression = & $Python -B -m pytest `
        (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests') `
        -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) {
        $Regression | Write-Host
        throw 'BLOCK_REGRESSION_TESTS'
    }

    $TargetedText = $Targeted -join "`n"
    $RegressionText = $Regression -join "`n"
    $TargetedCount = [regex]::Match($TargetedText, '(\d+) passed').Groups[1].Value
    $RegressionCount = [regex]::Match($RegressionText, '(\d+) passed').Groups[1].Value

    Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
    Write-Host "PATCH: $PatchId"
    Write-Host "TARGETED: $TargetedCount passed"
    Write-Host "REGRESSION: $RegressionCount passed"
    Write-Host 'OLD_EVIDENCE_DELETED: False'
    Write-Host 'BASELINE_CAPTURED: False'
    Write-Host 'REALITY_UNCHANGED: True'
    Write-Host 'VERDICT: COMMITTED_HEAD_BASELINE_SUPPORT_READY_FOR_COMMIT'
}
catch {
    Restore-Local
    Write-Host "PATCH: $PatchId" -ForegroundColor Red
    Write-Host 'VERDICT: RESTORED_AFTER_BLOCK' -ForegroundColor Red
    throw
}
