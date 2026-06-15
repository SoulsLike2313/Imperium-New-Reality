[CmdletBinding()]
param(
    [ValidateSet('launcher', 'gui', 'tui', 'smoke', 'status', 'supervisor-smoke')]
    [string]$Surface = 'launcher',
    [string]$Root = $env:IMPERIUM_ROOT
)

$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw 'Python is required on PATH.' }
if ($Root) { $env:IMPERIUM_ROOT = $Root }

switch ($Surface) {
    'launcher' { & $python.Source (Join-Path $PSScriptRoot '../LAUNCHER/imperial_launcher.py') }
    'gui' { & $python.Source (Join-Path $PSScriptRoot 'GUI/imperial_gui_workbench.py') }
    'tui' { & $python.Source (Join-Path $PSScriptRoot 'TUI/imperial_tui.py') }
    'smoke' { & $python.Source (Join-Path $PSScriptRoot 'TUI/imperial_tui.py') --smoke }
    'status' { & $python.Source (Join-Path $PSScriptRoot 'GUI/imperial_gui_workbench.py') --smoke }
    'supervisor-smoke' { & (Join-Path $PSScriptRoot 'SERVITORS/servitor_capsule_supervisor.ps1') -Smoke }
}
