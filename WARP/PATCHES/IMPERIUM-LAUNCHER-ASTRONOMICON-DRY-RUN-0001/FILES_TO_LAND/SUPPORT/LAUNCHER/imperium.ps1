param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $ImperiumArgs
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Cli = Join-Path $PSScriptRoot "imperium_cli.py"

if (-not (Test-Path $Cli)) {
  throw "imperium_cli.py not found: $Cli"
}

python $Cli --repo-root $RepoRoot @ImperiumArgs
exit $LASTEXITCODE
