$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$PatchId = 'IMPERIUM_PHASE6_TOOL_PATH_IDENTITY_FIX_0004'
$ExpectedHead = '8f34f78f6dc36b82989ac51e2e2baedba26872de'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$ExpectedBranch = 'servitor/imperium-core-reference-corridor-0001'
$ExpectedRoot = ([IO.Path]::GetFullPath('E:\IMPERIUM_WARPS\IMPERIUM-CORE-REFERENCE-CORRIDOR-0001')).Replace('/','\').TrimEnd('\')
$Root = (git rev-parse --show-toplevel).Trim()
$ActualRoot = ([IO.Path]::GetFullPath($Root)).Replace('/','\').TrimEnd('\')
$PatchRoot = Join-Path $Root "WARP/PATCHES/$PatchId"
$Validator = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py'
$Test = Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase6_tool_path_identity.py'
$PayloadValidator = Join-Path $PatchRoot 'payload/ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/phase6_live_ui_validation.py'
$PayloadTest = Join-Path $PatchRoot 'payload/ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_phase6_tool_path_identity.py'
$Report = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$Hardening = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Baseline = Join-Path $Hardening 'PHASE6_LIVE_UI_BASELINE.json'
$LiveIndex = Join-Path $Report 'live_ui_evidence/EVIDENCE_INDEX.json'
$Receipt = Join-Path $Hardening 'LIVE_UI_ACTION_RECEIPT.json'
$Proof = Join-Path $Hardening 'LIVE_UI_CORRIDOR_PROOF.md'
$Reality = 'E:\IMPERIUM_REALITY'
$Backup = Join-Path $PatchRoot 'runtime_backup_phase6_live_ui_validation.py'
function Restore-LocalFix {
    if (Test-Path $Backup) { Copy-Item $Backup $Validator -Force }
    Remove-Item $Test -Force -ErrorAction SilentlyContinue
    Remove-Item $Receipt -Force -ErrorAction SilentlyContinue
    Remove-Item $Proof -Force -ErrorAction SilentlyContinue
}
try {
    if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
    if ($ActualRoot -ine $ExpectedRoot) { throw "BLOCK_WRONG_WARP: $Root" }
    if ((git rev-parse HEAD).Trim() -ne $ExpectedHead) { throw 'BLOCK_WARP_HEAD_MISMATCH' }
    if ((git branch --show-current).Trim() -ne $ExpectedBranch) { throw 'BLOCK_BRANCH_MISMATCH' }
    if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }
    foreach ($required in @($Validator,$PayloadValidator,$PayloadTest,$Baseline,$LiveIndex)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "BLOCK_REQUIRED_FILE_MISSING: $required" }
    }
    $Live = Get-Content -Raw $LiveIndex | ConvertFrom-Json
    $LiveCount = @($Live.entries.PSObject.Properties).Count
    if ($LiveCount -ne 1) { throw "BLOCK_EXPECTED_EXACTLY_ONE_EXISTING_LIVE_EVIDENCE: $LiveCount" }
    Copy-Item $Validator $Backup -Force
    Copy-Item $PayloadValidator $Validator -Force
    Copy-Item $PayloadTest $Test -Force
    $Python = (Get-Command python.exe -ErrorAction Stop).Source
    $Targeted = & $Python -B -m pytest $Test (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_live_ui_evidence.py') (Join-Path $Root 'ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_pinned_tools.py') -q -p no:cacheprovider 2>&1
    if ($LASTEXITCODE -ne 0) { $Targeted | Write-Host; throw 'BLOCK_TARGETED_TESTS' }
    $TargetedText = $Targeted -join "`n"
    $Match = [regex]::Match($TargetedText,'(\d+) passed')
    if (-not $Match.Success) { throw 'BLOCK_TARGETED_TEST_COUNT' }
    $TargetedPass = [int]$Match.Groups[1].Value
    & $Python -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation --mode verify --repo $Root --reality $Reality --corridor-report $Report --baseline $Baseline --hardening-report $Hardening
    if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE6_VERIFY' }
    $Value = Get-Content -Raw $Receipt | ConvertFrom-Json
    if ($Value.verdict -ne 'LIVE_UI_CORRIDOR_PROVEN') { throw 'BLOCK_PHASE6_RECEIPT_VERDICT' }
    if ($Value.live_count_before -ne 0 -or $Value.live_count_after -ne 1) { throw 'BLOCK_LIVE_COUNT' }
    if ($Value.tool_path_identity_rule -ne 'OS_SAMEFILE_OR_WINDOWS_EXTENDED_PATH_NORMALIZATION') { throw 'BLOCK_PATH_IDENTITY_RULE' }
    if ($Value.path_resolution_used -ne $false) { throw 'BLOCK_PATH_RESOLUTION_USED' }
    if ($Value.phase3_surface_verdict -ne 'LEGACY_MUTATION_SURFACE_CLOSED') { throw 'BLOCK_PHASE3_REGRESSION' }
    if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_CHANGED' }
    Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
    Write-Host "PATCH: $PatchId"
    Write-Host "TARGETED_TESTS: $TargetedPass passed"
    Write-Host "ACTION_REQUEST: $($Value.action_request_id)"
    Write-Host "EVIDENCE: $($Value.evidence_id)"
    Write-Host "LIVE_COUNT: $($Value.live_count_before) -> $($Value.live_count_after)"
    Write-Host "TOOL_PATH_IDENTITY: $($Value.tool_path_identity_rule)"
    Write-Host "PATH_RESOLUTION_USED: $($Value.path_resolution_used)"
    Write-Host "PHASE3_SURFACE: $($Value.phase3_surface_verdict)"
    Write-Host "REALITY_UNCHANGED: $($Value.reality_unchanged)"
    Write-Host "RECEIPT: $Receipt"
    Write-Host 'VERDICT: LIVE_UI_CORRIDOR_PROVEN'
}
catch {
    Restore-LocalFix
    Write-Host "PATCH: $PatchId" -ForegroundColor Red
    Write-Host 'VERDICT: RESTORED_AFTER_BLOCK' -ForegroundColor Red
    throw
}
