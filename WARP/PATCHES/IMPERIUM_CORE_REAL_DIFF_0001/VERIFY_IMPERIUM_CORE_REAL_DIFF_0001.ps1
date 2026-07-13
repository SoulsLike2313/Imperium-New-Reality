$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ExpectedBase = '281c3a7c8463de7fb64473929fe0ed975f99f595'
$Repo = (& git -C (Get-Location).Path rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw 'BLOCK_NOT_GIT_REPO' }
$Reality = 'E:\IMPERIUM_REALITY'
if ($PSVersionTable.PSVersion.ToString() -ne '7.6.2') { throw 'BLOCK_PWSH_VERSION' }
if ((& git -C $Reality rev-parse HEAD).Trim() -ne $ExpectedBase) { throw 'BLOCK_REALITY_HEAD_MISMATCH' }
if ((& git -C $Reality status --porcelain=v1)) { throw 'BLOCK_REALITY_DIRTY' }
$env:PYTHONDONTWRITEBYTECODE = '1'
$targeted = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_real_diff.py ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests/test_ui_contract.py -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $targeted | Write-Host; throw 'BLOCK_TARGETED_TESTS' }
$regression = & python -B -m pytest ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/tests -q -p no:cacheprovider 2>&1
if ($LASTEXITCODE -ne 0) { $regression | Write-Host; throw 'BLOCK_REGRESSION_TESTS' }
$receiptPath = Join-Path $Repo 'ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002/REAL_DIFF_RECEIPT.json'
if (-not (Test-Path $receiptPath)) { throw 'BLOCK_RECEIPT_MISSING' }
$receipt = Get-Content -Raw $receiptPath | ConvertFrom-Json
Write-Host "PATCH: IMPERIUM_CORE_REAL_DIFF_0001"
Write-Host "TESTS: $($targeted -join ' ') | $($regression -join ' ')"
Write-Host "REALITY_UNCHANGED: true"
Write-Host "RECEIPT: $receiptPath"
Write-Host "VERDICT: $($receipt.verdict)"
