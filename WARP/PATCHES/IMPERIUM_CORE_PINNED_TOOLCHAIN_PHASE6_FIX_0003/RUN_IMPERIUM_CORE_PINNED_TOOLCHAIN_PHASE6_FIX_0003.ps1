$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_CORE_PINNED_TOOLCHAIN_PHASE6_FIX_0003'
$ExpectedHead = '8f34f78f6dc36b82989ac51e2e2baedba26872de'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$Registry = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001/CAPABILITY_REGISTRY.json'
$HardeningReport = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$CorridorReport = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Baseline = Join-Path $HardeningReport 'PHASE6_LIVE_UI_BASELINE.json'
$ToolReceipt = Join-Path $HardeningReport 'PINNED_TOOLCHAIN_RECEIPT.json'
$Reality = 'E:\IMPERIUM_REALITY'

function Restore-NewChanges {
    if (Test-Path $BackupRoot) {
        Get-ChildItem (Join-Path $BackupRoot 'files') -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
            $relative = [IO.Path]::GetRelativePath((Join-Path $BackupRoot 'files'), $_.FullName)
            $destination = Join-Path $Root $relative
            New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
            Copy-Item $_.FullName $destination -Force
        }
        $newList = Join-Path $BackupRoot 'new_files.txt'
        if (Test-Path $newList) {
            Get-Content $newList | Where-Object { $_ } | ForEach-Object {
                Remove-Item (Join-Path $Root $_) -Force -ErrorAction SilentlyContinue
            }
        }
        if (Test-Path (Join-Path $BackupRoot 'CAPABILITY_REGISTRY.json')) {
            Copy-Item (Join-Path $BackupRoot 'CAPABILITY_REGISTRY.json') $Registry -Force
        }
    }
    Remove-Item $Baseline, $ToolReceipt -Force -ErrorAction SilentlyContinue
}

try {
    if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
    $ExpectedWarpPath = ([IO.Path]::GetFullPath('E:\IMPERIUM_WARPS\IMPERIUM-CORE-REFERENCE-CORRIDOR-0001')).Replace('/', '\\').TrimEnd('\\')
    $ActualWarpPath = ([IO.Path]::GetFullPath($Root)).Replace('/', '\\').TrimEnd('\\')
    if ($ActualWarpPath -ine $ExpectedWarpPath) { throw "BLOCK_WRONG_WARP: $Root" }
    if ((git rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
    if ((git branch --show-current).Trim() -ne $ExpectedBranch) { throw 'BLOCK_BRANCH_MISMATCH' }
    if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }

    foreach ($required in @(
        'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/live_ui_evidence.py',
        'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py',
        'WARP/PATCHES/IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002'
    )) {
        if (-not (Test-Path (Join-Path $Root $required))) { throw "BLOCK_PHASE6_FIX2_STATE_MISSING: $required" }
    }

    Remove-Item $BackupRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path (Join-Path $BackupRoot 'files') -Force | Out-Null
    Copy-Item $Registry (Join-Path $BackupRoot 'CAPABILITY_REGISTRY.json') -Force
    $newFiles = [System.Collections.Generic.List[string]]::new()
    Get-ChildItem (Join-Path $PatchRoot 'payload') -Recurse -File | ForEach-Object {
        $relative = [IO.Path]::GetRelativePath((Join-Path $PatchRoot 'payload'), $_.FullName)
        $destination = Join-Path $Root $relative
        if (Test-Path $destination) {
            $backup = Join-Path (Join-Path $BackupRoot 'files') $relative
            New-Item -ItemType Directory -Path (Split-Path $backup) -Force | Out-Null
            Copy-Item $destination $backup -Force
        } else {
            $newFiles.Add($relative)
        }
        New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
        Copy-Item $_.FullName $destination -Force
    }
    $newFiles | Set-Content (Join-Path $BackupRoot 'new_files.txt') -Encoding utf8

    $GitPath = (Get-Command git.exe -ErrorAction Stop).Source
    $PwshPath = (Get-Process -Id $PID).Path
    $GitHash = (Get-FileHash $GitPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $PwshHash = (Get-FileHash $PwshPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $PythonPath = (Get-Command python.exe -ErrorAction Stop).Source

    $env:IMPERIUM_PINNED_TOOLCHAIN_REQUIRED = '1'
    $env:IMPERIUM_GIT_EXECUTABLE = $GitPath
    $env:IMPERIUM_GIT_SHA256 = $GitHash
    $env:IMPERIUM_PWSH_EXECUTABLE = $PwshPath
    $env:IMPERIUM_PWSH_SHA256 = $PwshHash
    $env:PYTHONDONTWRITEBYTECODE = '1'

    & $PythonPath -B (Join-Path $PatchRoot 'tools/update_registry.py') `
        --registry $Registry --git $GitPath --pwsh $PwshPath --worktree $Root --reality $Reality
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_REGISTRY_UPDATE' }

    $targeted = & $PythonPath -B -m pytest `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_pinned_tools.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_root_resolver.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_real_diff.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_executor.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_live_ui_evidence.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_tauri_surface.py `
        -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) { $targeted | Write-Host; throw 'BLOCK_TARGETED_TESTS' }

    $regression = & $PythonPath -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) { $regression | Write-Host; throw 'BLOCK_REGRESSION_TESTS' }

    cargo test --manifest-path SUPPORT/APP_TAURI/src-tauri/Cargo.toml
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_RUST_TESTS' }
    cargo check --manifest-path SUPPORT/APP_TAURI/src-tauri/Cargo.toml
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_CARGO_CHECK' }
    Push-Location SUPPORT/APP_TAURI
    try { npm run build; if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NPM_BUILD' } }
    finally { Pop-Location }

    $OldPath = $env:PATH
    try {
        $env:PATH = ''
        $snapshotRaw = & $PythonPath -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.cli ui-snapshot 2>&1
        $snapshotExit = $LASTEXITCODE
    } finally { $env:PATH = $OldPath }
    if ($snapshotExit -ne 0) { $snapshotRaw | Write-Host; throw 'BLOCK_PINNED_UI_SNAPSHOT' }
    $snapshot = ($snapshotRaw -join "`n") | ConvertFrom-Json
    if ($snapshot.backend_truth -ne $true) { throw 'BLOCK_UI_SNAPSHOT_NOT_BACKEND_TRUTH' }

    $toolReceiptValue = [ordered]@{
        schema_version = 'imperium.pinned_toolchain_receipt.v1'
        verdict = 'PINNED_TOOLCHAIN_PROVEN'
        implementation_head = $ExpectedHead
        git = [ordered]@{ executable = $GitPath; sha256 = $GitHash; path_resolution_used = $false }
        pwsh = [ordered]@{ executable = $PwshPath; sha256 = $PwshHash; version = $PSVersionTable.PSVersion.ToString(); path_resolution_used = $false }
        path_inherited_by_bridge = $false
        reality_head = $ExpectedReality
        reality_clean = $true
    }
    $toolReceiptValue | ConvertTo-Json -Depth 8 | Set-Content $ToolReceipt -Encoding utf8

    Remove-Item $Baseline -Force -ErrorAction SilentlyContinue
    & $PythonPath -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation `
        --mode baseline --repo $Root --reality $Reality --corridor-report $CorridorReport --baseline $Baseline
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE6_BASELINE' }

    $targetedCount = ([regex]::Match(($targeted -join "`n"), '(\d+) passed')).Groups[1].Value
    $regressionCount = ([regex]::Match(($regression -join "`n"), '(\d+) passed')).Groups[1].Value
    Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
    Write-Host "PATCH: $PatchId"
    Write-Host "GIT: $GitPath"
    Write-Host "GIT_SHA256: $GitHash"
    Write-Host "PWSH: $PwshPath"
    Write-Host "PWSH_SHA256: $PwshHash"
    Write-Host "TESTS: targeted=$targetedCount regression=$regressionCount"
    Write-Host 'PATH_INHERITED_BY_BRIDGE: False'
    Write-Host 'REALITY_UNCHANGED: True'
    Write-Host "BASELINE: $Baseline"
    Write-Host 'VERDICT: LIVE_UI_BASELINE_CAPTURED_WAITING_FOR_OWNER_ACTION'
}
catch {
    Restore-NewChanges
    Write-Host "PATCH: $PatchId" -ForegroundColor Red
    Write-Host "VERDICT: RESTORED_AFTER_BLOCK" -ForegroundColor Red
    throw
}
