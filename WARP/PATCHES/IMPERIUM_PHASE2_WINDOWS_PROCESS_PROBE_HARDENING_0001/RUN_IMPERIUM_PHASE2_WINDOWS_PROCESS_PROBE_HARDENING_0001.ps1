$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_PHASE2_WINDOWS_PROCESS_PROBE_HARDENING_0001'
$ExpectedHead = '8f34f78f6dc36b82989ac51e2e2baedba26872de'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$Root = (git rev-parse --show-toplevel).Trim()
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$Reality = 'E:\IMPERIUM_REALITY'
$ReportRoot = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Receipt = Join-Path $ReportRoot 'PHASE2_WINDOWS_PROCESS_PROBE_RECEIPT.json'

function Restore-PatchChanges {
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
    }
    Remove-Item $Receipt -Force -ErrorAction SilentlyContinue
}

$OldUtf8 = $env:PYTHONUTF8
$OldIoEncoding = $env:PYTHONIOENCODING
$OldNoBytecode = $env:PYTHONDONTWRITEBYTECODE

try {
    if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
    $ExpectedWarpPath = ([IO.Path]::GetFullPath('E:\IMPERIUM_WARPS\IMPERIUM-CORE-REFERENCE-CORRIDOR-0001')).Replace('/', '\').TrimEnd('\')
    $ActualWarpPath = ([IO.Path]::GetFullPath($Root)).Replace('/', '\').TrimEnd('\')
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

    # Reproduce the exact hostile encoding mode that exposed the defect.
    $env:PYTHONUTF8 = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $PythonPath = (Get-Command python.exe -ErrorAction Stop).Source

    $targeted = & $PythonPath -B -m pytest `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_windows_process_probe.py `
        ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_negative_proof.py `
        -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) { $targeted | Write-Host; throw 'BLOCK_TARGETED_TESTS' }

    $countMatch = [regex]::Match(($targeted -join "`n"), '(\d+) passed')
    if (-not $countMatch.Success) { throw 'BLOCK_TARGETED_COUNT' }
    $targetedCount = [int]$countMatch.Groups[1].Value

    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_CHANGED' }

    $value = [ordered]@{
        schema_version = 'imperium.phase2.windows_process_probe_receipt.v1'
        verdict = 'PHASE2_WINDOWS_PROCESS_PROBE_HARDENED'
        implementation_base_head = $ExpectedHead
        python_utf8_mode = $true
        observation_mode = 'TASKLIST_BYTES_ASCII_PID_TOKEN'
        targeted_tests_passed = $targetedCount
        reality_head = $ExpectedReality
        reality_clean = $true
    }
    New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
    $value | ConvertTo-Json -Depth 8 | Set-Content $Receipt -Encoding utf8

    Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
    Write-Host "PATCH: $PatchId"
    Write-Host 'PYTHON_UTF8_REPRODUCED: True'
    Write-Host "TESTS_PASS: $targetedCount"
    Write-Host 'REALITY_UNCHANGED: True'
    Write-Host "RECEIPT: $Receipt"
    Write-Host 'VERDICT: PHASE2_WINDOWS_PROCESS_PROBE_HARDENED'
}
catch {
    Restore-PatchChanges
    Write-Host "PATCH: $PatchId" -ForegroundColor Red
    Write-Host 'VERDICT: RESTORED_AFTER_BLOCK' -ForegroundColor Red
    throw
}
finally {
    if ($null -eq $OldUtf8) { Remove-Item Env:PYTHONUTF8 -ErrorAction SilentlyContinue } else { $env:PYTHONUTF8 = $OldUtf8 }
    if ($null -eq $OldIoEncoding) { Remove-Item Env:PYTHONIOENCODING -ErrorAction SilentlyContinue } else { $env:PYTHONIOENCODING = $OldIoEncoding }
    if ($null -eq $OldNoBytecode) { Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue } else { $env:PYTHONDONTWRITEBYTECODE = $OldNoBytecode }
}
