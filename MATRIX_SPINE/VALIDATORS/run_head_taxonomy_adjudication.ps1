$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$reportDir = Join-Path $repoRoot "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-HEAD-TAXONOMY-AND-COMBINED-REVIEW-ADJUDICATION-VM3-V0_1"

python3 (Join-Path $scriptDir "run_head_taxonomy_adjudication.py") `
  --repo-root $repoRoot `
  --report-dir $reportDir `
  @args
