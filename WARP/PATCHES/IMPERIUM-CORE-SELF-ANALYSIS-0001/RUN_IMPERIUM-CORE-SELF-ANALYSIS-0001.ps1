$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.ToString() -ne "7.6.2") {
  Write-Host "IMPERIUM SHELL: expected pwsh 7.6.2, got $($PSVersionTable.PSVersion)" -ForegroundColor Yellow
} else {
  Write-Host "IMPERIUM SHELL: pwsh 7.6.2 OK" -ForegroundColor Green
}

$PatchId = "IMPERIUM-CORE-SELF-ANALYSIS-0001"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptRoot "../../..")
$FilesToLand = Join-Path $ScriptRoot "FILES_TO_LAND"

Write-Host "TASK: $PatchId"

if (-not (Test-Path $FilesToLand)) {
  throw "FILES_TO_LAND missing: $FilesToLand"
}

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

$Validator = Join-Path $RepoRoot "SUPPORT/APP_TAURI/tests/validate_imperium_core_self_analysis.py"
python $Validator --repo-root $RepoRoot --apply
$Code = $LASTEXITCODE

$SummaryPath = Join-Path $RepoRoot "SUPPORT/APP_TAURI/receipts/imperium_core_self_analysis_summary.json"
if (Test-Path $SummaryPath) {
  $s = Get-Content $SummaryPath -Raw | ConvertFrom-Json
  Write-Host "VERDICT: $($s.verdict)"
  Write-Host "ASTRA: packs=$($s.astronomicon.pack_count) standard=$($s.astronomicon.standard_pack_count) candidate=$($s.astronomicon.candidate_pack_count) legacy=$($s.astronomicon.legacy_or_incomplete_count) dirty=$($s.astronomicon.dirty_nested_warp_count)"
  Write-Host "MECH: files=$($s.mechanicus.file_count) lines=$($s.mechanicus.total_lines) monoliths=$($s.mechanicus.monolith_risk_count) blockers=$($s.mechanicus.blocking_monolith_count) nodes=$($s.mechanicus.node_boundary_count)"
  Write-Host "NEXT: $($s.next_recommended_patch)"
  Write-Host "SUMMARY: SUPPORT/APP_TAURI/receipts/imperium_core_self_analysis_summary.json"
  Write-Host "RECEIPT: SUPPORT/APP_TAURI/receipts/imperium_core_self_analysis_receipt.json"
}

if ($Code -ne 0) {
  throw "$PatchId failed with exit code $Code"
}
