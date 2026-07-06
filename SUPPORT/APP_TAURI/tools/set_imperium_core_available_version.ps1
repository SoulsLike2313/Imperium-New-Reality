param(
  [string]$Version,
  [string]$Notes = "Terminal patch staged a new Imperium Core version.",
  [string]$RepoRoot = "."
)
if (-not $Version) { throw "Version is required" }
python "$PSScriptRoot/set_imperium_core_available_version.py" --repo-root $RepoRoot --version $Version --notes $Notes
