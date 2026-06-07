# run_imperial_ide_ops.ps1 - launch the Imperial IDE operational TUI on PC.
# Place under ORGANS/IMPERIAL_IDE/ after integration.
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..\..").Path
$env:IMPERIUM_ROOT = $RepoRoot
$Tui = Join-Path $RepoRoot "ORGANS\IMPERIAL_IDE\OPS\TUI\imperial_ide_ops_tui.py"
if (-Not (Test-Path $Tui)) {
    $Tui = Join-Path $PSScriptRoot "..\TUI\imperial_ide_ops_tui.py"
}
Write-Host "IMPERIUM_ROOT = $env:IMPERIUM_ROOT"
Write-Host "Launching Imperial IDE operational console..."
python $Tui
