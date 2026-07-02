param(
  [string]$Action = "",
  [switch]$ListActions
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Py = Join-Path $PSScriptRoot "imperium_tui.py"

if ($ListActions) {
  python $Py --repo-root $RepoRoot --list-actions
  exit $LASTEXITCODE
}

if ($Action -ne "") {
  python $Py --repo-root $RepoRoot --action $Action
  exit $LASTEXITCODE
}

python $Py --repo-root $RepoRoot
exit $LASTEXITCODE
