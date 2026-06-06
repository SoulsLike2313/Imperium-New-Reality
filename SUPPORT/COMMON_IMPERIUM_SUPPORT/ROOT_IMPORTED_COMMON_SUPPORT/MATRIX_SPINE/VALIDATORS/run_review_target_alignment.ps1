$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$reportDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-INDEPENDENT-REPLAY-AND-HEAD-CHAIN-RECONCILIATION-VM3-V0_1"

python3 (Join-Path $scriptDir "run_review_target_alignment.py") `
  --repo-root $repoRoot `
  --report-dir $reportDir `
  @args
