$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PatchId = 'IMPERIUM_CORE_PINNED_TOOLCHAIN_PHASE6_FIX_0003'
$Root = (git rev-parse --show-toplevel).Trim()
$Reality = 'E:\IMPERIUM_REALITY'
$ExpectedReality = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$CorridorReport = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-0001'
$HardeningReport = Join-Path $Root 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002'
$Baseline = Join-Path $HardeningReport 'PHASE6_LIVE_UI_BASELINE.json'
$RegistryPath = Join-Path $CorridorReport 'CAPABILITY_REGISTRY.json'
$PythonPath = (Get-Command python.exe -ErrorAction Stop).Source

if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
if ((git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedReality) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if (git -C $Reality status --porcelain=v1) { throw 'BLOCK_REALITY_DIRTY' }
if (-not (Test-Path $Baseline)) { throw 'BLOCK_PHASE6_BASELINE_MISSING' }

$registry = Get-Content -Raw $RegistryPath | ConvertFrom-Json
$gitCapability = $registry.capabilities | Where-Object capability_id -eq 'CORE_GIT'
$pwshCapability = $registry.capabilities | Where-Object capability_id -eq 'CORE_PWSH'
if (-not $gitCapability -or -not $pwshCapability) { throw 'BLOCK_PINNED_CAPABILITY_MISSING' }
$env:IMPERIUM_PINNED_TOOLCHAIN_REQUIRED = '1'
$env:IMPERIUM_GIT_EXECUTABLE = $gitCapability.executable_path
$env:IMPERIUM_GIT_SHA256 = $gitCapability.executable_sha256
$env:IMPERIUM_PWSH_EXECUTABLE = $pwshCapability.executable_path
$env:IMPERIUM_PWSH_SHA256 = $pwshCapability.executable_sha256
$env:PYTHONDONTWRITEBYTECODE = '1'

& $PythonPath -B -m ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase6_live_ui_validation `
    --mode verify --repo $Root --reality $Reality --corridor-report $CorridorReport `
    --baseline $Baseline --hardening-report $HardeningReport
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_PHASE6_VERIFY' }

$phase3 = & $PythonPath -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_tauri_surface.py -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $phase3 | Write-Host; throw 'BLOCK_PHASE3_REGRESSION' }
$targeted = & $PythonPath -B -m pytest `
    ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_pinned_tools.py `
    ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_live_ui_evidence.py `
    ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_root_resolver.py `
    ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_real_diff.py `
    -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $targeted | Write-Host; throw 'BLOCK_TARGETED_REVERIFY' }

$receipt = Get-Content -Raw (Join-Path $HardeningReport 'LIVE_UI_ACTION_RECEIPT.json') | ConvertFrom-Json
if ($receipt.verdict -ne 'LIVE_UI_CORRIDOR_PROVEN') { throw 'BLOCK_PHASE6_VERDICT' }
if ($receipt.reality_unchanged -ne $true) { throw 'BLOCK_REALITY_PROOF' }
if ($receipt.path_resolution_used -ne $false) { throw 'BLOCK_PATH_RESOLUTION_USED' }
if ((Get-FileHash $gitCapability.executable_path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $gitCapability.executable_sha256.ToLowerInvariant()) { throw 'BLOCK_GIT_HASH_CHANGED' }
if ((Get-FileHash $pwshCapability.executable_path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pwshCapability.executable_sha256.ToLowerInvariant()) { throw 'BLOCK_PWSH_HASH_CHANGED' }

Write-Host 'IMPERIUM SHELL: pwsh 7.6.2 OK' -ForegroundColor Green
Write-Host "PATCH: $PatchId"
Write-Host "ACTION_REQUEST: $($receipt.action_request_id)"
Write-Host "EVIDENCE: $($receipt.evidence_id)"
Write-Host "LIVE_COUNT: $($receipt.live_count_before) -> $($receipt.live_count_after)"
Write-Host "PINNED_GIT: $($receipt.pinned_git.executable)"
Write-Host "PINNED_PWSH: $($receipt.pinned_pwsh.executable)"
Write-Host 'PATH_RESOLUTION_USED: False'
Write-Host "PHASE3_SURFACE: $($receipt.phase3_surface_verdict)"
Write-Host 'REALITY_UNCHANGED: True'
Write-Host "RECEIPT: $(Join-Path $HardeningReport 'LIVE_UI_ACTION_RECEIPT.json')"
Write-Host 'VERDICT: LIVE_UI_CORRIDOR_PROVEN'
