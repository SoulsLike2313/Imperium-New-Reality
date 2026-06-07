param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ImperialIdeArgs
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Cli = Join-Path $RepoRoot 'ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py'
$Tui = Join-Path $RepoRoot 'ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_tui.py'

Push-Location $RepoRoot
try {
  if (-not $ImperialIdeArgs -or $ImperialIdeArgs.Count -eq 0) {
    & python $Tui
  } elseif ($ImperialIdeArgs[0] -eq '--smoke') {
    & python $Tui --smoke
  } else {
    & python $Cli @ImperialIdeArgs
  }
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
