[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction Stop
$env:IMPERIUM_ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
& $python.Source (Join-Path $PSScriptRoot 'METAOS/metaos_smoke.py')
