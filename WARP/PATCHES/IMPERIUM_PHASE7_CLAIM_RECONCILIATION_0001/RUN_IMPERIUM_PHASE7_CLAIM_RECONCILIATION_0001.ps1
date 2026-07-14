$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_PHASE7_CLAIM_RECONCILIATION_0001'
$ExpectedHead = 'dc3079e4ac9e299761317d6bc078ce1ac3f18c8d'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$Root = (git rev-parse --show-toplevel).Trim()
$Reality = 'E:\IMPERIUM_REALITY'
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Payload = Join-Path $PatchRoot 'payload'
$Runtime = Join-Path $PatchRoot 'runtime'
$Report = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Backup = Join-Path $PatchRoot 'runtime_backup'

$PayloadFiles = @(
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/ui_snapshot.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase7_claim_reconciliation.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase7_disk_auditor.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_claim_reconciliation.py',
    'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_ui_truth.py',
    'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/KNOWN_GAPS.md',
    'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/KNOWN_GAPS.md'
)

function Restore-Payload {
    foreach ($Relative in $PayloadFiles) {
        $Target = Join-Path $Root $Relative
        $Saved = Join-Path $Backup $Relative
        if (Test-Path $Saved -PathType Leaf) {
            New-Item -ItemType Directory -Path (Split-Path $Target) -Force | Out-Null
            Copy-Item $Saved $Target -Force
        }
        else {
            Remove-Item $Target -Force -ErrorAction SilentlyContinue
        }
    }
}

try {
    if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
    if ((git rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
    if ((git branch --show-current).Trim() -ne $ExpectedBranch) { throw 'BLOCK_BRANCH_MISMATCH' }
    if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }

    $Status = @(git status --porcelain=v1)
    $Unexpected = @(
        $Status | Where-Object {
            $_ -notmatch '^\?\? WARP/PATCHES/IMPERIUM_PHASE7_CLAIM_RECONCILIATION_0001/'
        }
    )
    if ($Unexpected) {
        $Unexpected | Write-Host
        throw 'BLOCK_UNEXPECTED_PREEXISTING_WARP_CHANGES'
    }

    Remove-Item $Backup -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item $Runtime -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $Backup,$Runtime -Force | Out-Null

    foreach ($Relative in $PayloadFiles) {
        $Target = Join-Path $Root $Relative
        $Source = Join-Path $Payload $Relative
        if (-not (Test-Path $Source -PathType Leaf)) { throw "BLOCK_PAYLOAD_MISSING: $Relative" }
        if (Test-Path $Target -PathType Leaf) {
            $Saved = Join-Path $Backup $Relative
            New-Item -ItemType Directory -Path (Split-Path $Saved) -Force | Out-Null
            Copy-Item $Target $Saved -Force
        }
        New-Item -ItemType Directory -Path (Split-Path $Target) -Force | Out-Null
        Copy-Item $Source $Target -Force
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

    $Targeted = & $Python -B -m pytest `
        (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_claim_reconciliation.py') `
        (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase7_ui_truth.py') `
        (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_ui_contract.py') `
        -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) {
        $Targeted | Write-Host
        throw 'BLOCK_PHASE7_TARGETED_TESTS'
    }

    $Regression = & $Python -B -m pytest `
        (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests') `
        -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) {
        $Regression | Write-Host
        throw 'BLOCK_PHASE7_REGRESSION'
    }

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
        --output-root $Runtime `
        --mode provisional
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PROVISIONAL_RECONCILIATION' }

    & $Python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase7_disk_auditor `
        --repo $Root `
        --reality $Reality `
        --corridor-report $Report `
        --hardening-report $Hardening `
        --claim-status (Join-Path $Runtime 'CURRENT_CLAIM_STATUS.json') `
        --output (Join-Path $Runtime 'PHASE7_INDEPENDENT_DISK_AUDIT.json') `
        --mode provisional
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PROVISIONAL_DISK_AUDIT' }

    $Claim = Get-Content -Raw (Join-Path $Runtime 'PHASE7_CLAIM_RECONCILIATION_RECEIPT.json') | ConvertFrom-Json
    $Audit = Get-Content -Raw (Join-Path $Runtime 'PHASE7_INDEPENDENT_DISK_AUDIT.json') | ConvertFrom-Json
    if ($Claim.verdict -ne 'REFERENCE_CORRIDOR_PASS_WITH_DEBT') { throw "BLOCK_CLAIM_VERDICT: $($Claim.verdict)" }
    if ($Audit.verdict -ne 'REFERENCE_CORRIDOR_PASS_WITH_DEBT') { throw "BLOCK_AUDIT_VERDICT: $($Audit.verdict)" }

    $TargetedCount = [regex]::Match(($Targeted -join "`n"), '(\d+) passed').Groups[1].Value
    $RegressionCount = [regex]::Match(($Regression -join "`n"), '(\d+) passed').Groups[1].Value

    Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
    Write-Host "PATCH: $PatchId"
    Write-Host "TARGETED: $TargetedCount passed"
    Write-Host "REGRESSION: $RegressionCount passed"
    Write-Host 'RUST_TESTS: PASS'
    Write-Host 'CARGO_CHECK: PASS'
    Write-Host 'NPM_BUILD: PASS'
    Write-Host "PROVISIONAL_CLAIM: $($Claim.verdict)"
    Write-Host "PROVISIONAL_AUDIT: $($Audit.verdict)"
    Write-Host 'CURRENT_ORGAN_RING: NOT_PROVEN'
    Write-Host 'HISTORICAL_ORGAN_PASS_PROMOTED: False'
    Write-Host 'REALITY_UNCHANGED: True'
    Write-Host 'VERDICT: PHASE7_IMPLEMENTATION_READY_FOR_COMMIT'
}
catch {
    Restore-Payload
    Write-Host "PATCH: $PatchId" -ForegroundColor Red
    Write-Host 'VERDICT: RESTORED_AFTER_BLOCK' -ForegroundColor Red
    throw
}
