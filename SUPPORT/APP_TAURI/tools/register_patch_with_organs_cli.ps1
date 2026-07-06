param(
  [Parameter(Mandatory=$true)][string]$PatchId,
  [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"
python "SUPPORT/APP_TAURI/tools/register_patch_with_organs_cli.py" --repo-root $RepoRoot --patch-id $PatchId
