$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_CORE_REAL_DIFF_0001'
$ExpectedHead = 'f686b90ea0d2e1af06e2243dd543324f5be6c9e3'
$ExpectedRealityHead = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$PatchRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PayloadRoot = Join-Path $PatchRoot 'payload'
$BackupRoot = Join-Path $PatchRoot 'runtime_backup'
$ReceiptRootRel = 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'

function Invoke-Git([string]$Repo, [string[]]$Arguments) {
    $output = & git -C $Repo @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git $($Arguments -join ' ') failed: $output" }
    return ($output -join "`n").Trim()
}

$Repo = (Invoke-Git (Get-Location).Path @('rev-parse','--show-toplevel')).Trim()
$Repo = [System.IO.Path]::GetFullPath($Repo)
$Reality = 'E:\IMPERIUM_REALITY'

if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw "BLOCK_PWSH_VERSION: expected 7.6.2, got $($PSVersionTable.PSVersion)" }
if ((Invoke-Git $Repo @('rev-parse','HEAD')) -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
if ((Invoke-Git $Repo @('rev-parse','--abbrev-ref','HEAD')) -ne $ExpectedBranch) { throw 'BLOCK_WARP_BRANCH_MISMATCH' }
if ((Invoke-Git $Reality @('rev-parse','HEAD')) -ne $ExpectedRealityHead) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if ((Invoke-Git $Reality @('rev-parse','origin/master')) -ne $ExpectedRealityHead) { throw 'BLOCK_ORIGIN_MASTER_MISMATCH' }
if ((Invoke-Git $Reality @('status','--porcelain=v1'))) { throw 'BLOCK_REALITY_DIRTY' }

$statusLines = @(Invoke-Git $Repo @('status','--porcelain=v1') -split "`n" | Where-Object { $_ })
$unexpected = @($statusLines | Where-Object { $_ -notmatch '^\?\? WARP/PATCHES/IMPERIUM_CORE_REAL_DIFF_0001/' })
if ($unexpected.Count -gt 0) { throw "BLOCK_WARP_DIRTY_BEFORE_PATCH: $($unexpected -join '; ')" }

$manifest = Get-Content -Raw (Join-Path $PatchRoot 'MANIFEST.json') | ConvertFrom-Json
foreach ($entry in $manifest.payload_files) {
    $source = Join-Path $PayloadRoot $entry.path
    $actual = (Get-FileHash -Algorithm SHA256 $source).Hash.ToLowerInvariant()
    if ($actual -ne $entry.sha256) { throw "BLOCK_PAYLOAD_HASH: $($entry.path)" }
}
foreach ($entry in $manifest.preimages) {
    $target = Join-Path $Repo $entry.path
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "BLOCK_PREIMAGE_MISSING: $($entry.path)" }
    $actual = (Get-FileHash -Algorithm SHA256 $target).Hash.ToLowerInvariant()
    if ($actual -ne $entry.sha256) { throw "BLOCK_PREIMAGE_HASH: $($entry.path)" }
}

New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
foreach ($entry in $manifest.preimages) {
    $source = Join-Path $Repo $entry.path
    $backup = Join-Path $BackupRoot $entry.path
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
    Copy-Item -LiteralPath $source -Destination $backup -Force
}
foreach ($entry in $manifest.payload_files) {
    $source = Join-Path $PayloadRoot $entry.path
    $target = Join-Path $Repo $entry.path
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Force
}

$env:PYTHONDONTWRITEBYTECODE = '1'
$targetedOutput = & python -B -m pytest `
    ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_real_diff.py `
    ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_ui_contract.py `
    -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $targetedOutput | Write-Host; throw 'BLOCK_TARGETED_TESTS' }
$targetedText = $targetedOutput -join "`n"
$targetedMatch = [regex]::Match($targetedText, '(\d+) passed')
if (-not $targetedMatch.Success) { throw 'BLOCK_TARGETED_COUNT_UNPARSEABLE' }
$targetedPass = [int]$targetedMatch.Groups[1].Value

$regressionOutput = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $regressionOutput | Write-Host; throw 'BLOCK_REGRESSION_TESTS' }
$regressionText = $regressionOutput -join "`n"
$regressionMatch = [regex]::Match($regressionText, '(\d+) passed')
if (-not $regressionMatch.Success) { throw 'BLOCK_REGRESSION_COUNT_UNPARSEABLE' }
$regressionPass = [int]$regressionMatch.Groups[1].Value

Push-Location (Join-Path $Repo 'SUPPORT/APP_TAURI')
try {
    & npm run build *> (Join-Path $PatchRoot 'npm_build.log')
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NPM_BUILD' }
} finally { Pop-Location }

& cargo check --manifest-path (Join-Path $Repo 'SUPPORT/APP_TAURI/src-tauri/Cargo.toml') *> (Join-Path $PatchRoot 'cargo_check.log')
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_CARGO_CHECK' }

$ReportRoot = Join-Path $Repo $ReceiptRootRel
$validatorOutput = & python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase5_real_diff_validation `
    --repo $Repo --reality $Reality --report-root $ReportRoot `
    --targeted-pass $targetedPass --regression-pass $regressionPass `
    --npm-build PASS --cargo-check PASS 2>&1
if ($LASTEXITCODE -ne 0) { $validatorOutput | Write-Host; throw 'BLOCK_PHASE5_VALIDATOR' }

$receipt = Get-Content -Raw (Join-Path $ReportRoot 'REAL_DIFF_RECEIPT.json') | ConvertFrom-Json
Write-Host "PATCH: $PatchId"
Write-Host "BASE_HEAD: $($receipt.base_head)"
Write-Host "RESULT_HEAD: $($receipt.result_head_at_validation)"
Write-Host "FILES_CHANGED_COMMITTED: $($receipt.measured.files_changed)"
Write-Host "LINES: +$($receipt.measured.insertions) / -$($receipt.measured.deletions)"
Write-Host "TESTS: targeted=$targetedPass regression=$regressionPass"
Write-Host "REALITY_UNCHANGED: $([bool]($receipt.measured.reality_dirty_count -eq 0))"
Write-Host "RECEIPT: $(Join-Path $ReportRoot 'REAL_DIFF_RECEIPT.json')"
Write-Host "VERDICT: $($receipt.verdict)"
