[CmdletBinding()]
param(
    [ValidateSet('gui', 'tui', 'smoke', 'status', 'supervisor-smoke')]
    [string]$Surface = 'gui'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$env:IMPERIUM_ROOT = $repoRoot
& (Join-Path $PSScriptRoot 'WORKBENCH/run_imperial_workbench.ps1') -Surface $Surface -Root $repoRoot
