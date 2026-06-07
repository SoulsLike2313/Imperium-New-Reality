param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ImperialIdeArgs
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Cli = Join-Path $RepoRoot 'ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py'
$Tui = Join-Path $RepoRoot 'ORGANS\IMPERIAL_IDE\WORKBENCH\TUI\imperial_tui.py'
$Gui = Join-Path $RepoRoot 'ORGANS\IMPERIAL_IDE\WORKBENCH\GUI\imperial_gui_workbench.py'
$Launcher = Join-Path $RepoRoot 'ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py'

Push-Location $RepoRoot
try {
  if (-not $ImperialIdeArgs -or $ImperialIdeArgs.Count -eq 0) {
    & python $Launcher
  } else {
    $first = $ImperialIdeArgs[0].ToLowerInvariant()
    $rest = @()
    if ($ImperialIdeArgs.Count -gt 1) { $rest = $ImperialIdeArgs[1..($ImperialIdeArgs.Count - 1)] }

    switch ($first) {
      'launcher' { & python $Launcher @rest }
      '--launcher' { & python $Launcher @rest }
      'home' { & python $Launcher @rest }
      '--smoke' { & python $Launcher --smoke }
      'launcher-smoke' { & python $Launcher --smoke }
      'tui' { & python $Tui @rest }
      '--tui' { & python $Tui @rest }
      'gui' { & python $Gui @rest }
      '--gui' { & python $Gui @rest }
      'shell' { & python $Cli @rest }
      '--shell' { & python $Cli @rest }
      default { & python $Cli @ImperialIdeArgs }
    }
  }
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
