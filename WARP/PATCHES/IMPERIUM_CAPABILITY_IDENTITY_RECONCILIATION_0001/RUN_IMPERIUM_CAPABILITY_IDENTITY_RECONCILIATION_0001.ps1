$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_CAPABILITY_IDENTITY_RECONCILIATION_0001'
$ExpectedHead = '8f34f78f6dc36b82989ac51e2e2baedba26872de'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$Root = (git rev-parse --show-toplevel).Trim()
$ExpectedRoot = ([IO.Path]::GetFullPath('E:\IMPERIUM_WARPS\IMPERIUM-CORE-REFERENCE-CORRIDOR-0001')).Replace('/','\').TrimEnd('\')
$ActualRoot = ([IO.Path]::GetFullPath($Root)).Replace('/','\').TrimEnd('\')
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Registry = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Receipt = Join-Path $Hardening 'CAPABILITY_IDENTITY_RECONCILIATION_RECEIPT.json'
$Backup = Join-Path $PatchRoot 'runtime_backup_CAPABILITY_REGISTRY.json'
$Reality = 'E:\IMPERIUM_REALITY'

function Restore-Registry {
    if (Test-Path $Backup) {
        Copy-Item $Backup $Registry -Force
    }
    Remove-Item $Receipt -Force -ErrorAction SilentlyContinue
}

try {
    if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
    if ($ActualRoot -ine $ExpectedRoot) { throw "BLOCK_WRONG_WARP: $Root" }
    if ((git rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
    if ((git branch --show-current).Trim() -ne $ExpectedBranch) { throw 'BLOCK_BRANCH_MISMATCH' }
    if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }

    foreach ($required in @(
        'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/pinned_tools.py',
        'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/live_ui_evidence.py',
        'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/PHASE6_LIVE_UI_BASELINE.json',
        'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/PINNED_TOOLCHAIN_RECEIPT.json'
    )) {
        if (-not (Test-Path (Join-Path $Root $required))) { throw "BLOCK_REQUIRED_PHASE6_STATE_MISSING: $required" }
    }

    Copy-Item $Registry $Backup -Force
    $Python = (Get-Command python.exe -ErrorAction Stop).Source

    & $Python -B (Join-Path $PatchRoot 'tools/reconcile_registry.py') `
        --registry $Registry `
        --receipt $Receipt
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_CAPABILITY_RECONCILIATION' }

    $ToolReceipt = Get-Content -Raw (Join-Path $Hardening 'PINNED_TOOLCHAIN_RECEIPT.json') | ConvertFrom-Json
    $OldPath = $env:PATH
    try {
        $env:PATH = ''
        $env:IMPERIUM_ACTIVE_WORKTREE = $Root
        $env:IMPERIUM_PINNED_TOOLCHAIN_REQUIRED = '1'
        $env:IMPERIUM_GIT_EXECUTABLE = $ToolReceipt.git.executable
        $env:IMPERIUM_GIT_SHA256 = $ToolReceipt.git.sha256
        $env:IMPERIUM_PWSH_EXECUTABLE = $ToolReceipt.pwsh.executable
        $env:IMPERIUM_PWSH_SHA256 = $ToolReceipt.pwsh.sha256
        $env:PYTHONDONTWRITEBYTECODE = '1'
        $env:PYTHONIOENCODING = 'utf-8'
        $env:PYTHONNOUSERSITE = '1'
        $env:PYTHONUTF8 = '1'

        $RefreshRaw = & $Python -B `
            -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.cli `
            ui-action `
            --action-id refresh_state `
            --payload-json '{}' 2>&1
        $RefreshExit = $LASTEXITCODE
    }
    finally {
        $env:PATH = $OldPath
    }
    if ($RefreshExit -ne 0) {
        $RefreshRaw | Write-Host
        throw 'BLOCK_REFRESH_STATE_AFTER_RECONCILIATION'
    }

    $Refresh = ($RefreshRaw -join "`n") | ConvertFrom-Json
    if ($Refresh.verdict -eq 'BLOCK') { throw 'BLOCK_REFRESH_RETURNED_BLOCK' }

    $ReceiptValue = Get-Content -Raw $Receipt | ConvertFrom-Json
    if ($ReceiptValue.verdict -ne 'CAPABILITY_IDENTITY_RECONCILED') { throw 'BLOCK_RECEIPT_VERDICT' }
    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_CHANGED' }

    Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
    Write-Host "PATCH: $PatchId"
    Write-Host 'RECONCILED: CORE_REPORT_BUILDER, CORE_VALIDATION_SUITE'
    Write-Host "REGISTRY_DIGEST: $($ReceiptValue.registry_digest_after)"
    Write-Host 'REFRESH_STATE_WITH_EMPTY_PATH: PASS'
    Write-Host 'LIVE_DIAGNOSTIC_EXECUTED: False'
    Write-Host 'REALITY_UNCHANGED: True'
    Write-Host "RECEIPT: $Receipt"
    Write-Host 'VERDICT: CAPABILITY_IDENTITY_RECONCILED_READY_FOR_LIVE_UI_RETRY'
}
catch {
    Restore-Registry
    Write-Host "PATCH: $PatchId" -ForegroundColor Red
    Write-Host 'VERDICT: RESTORED_AFTER_BLOCK' -ForegroundColor Red
    throw
}
