[CmdletBinding()]
param(
    [ValidateSet('smoke', 'status', 'list', 'open', 'gate')]
    [string]$Command = 'status',
    [string]$Task = 'operator candidate task',
    [ValidateSet('CORE_CHANGE', 'IMPERIUM_FORCE', 'THIRD_PARTY')]
    [string]$Kind = 'THIRD_PARTY',
    [string]$Session
)

$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction Stop
$warpRoot = Join-Path $PSScriptRoot 'WARP'
$env:IMPERIUM_ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$env:WARP_ROOT = Join-Path $warpRoot 'runtime'

switch ($Command) {
    'smoke' { & $python.Source (Join-Path $warpRoot 'warp_smoke.py') }
    'status' { Get-Content -Raw (Join-Path $warpRoot 'INTEGRATION_STATUS.json') }
    'list' { & $python.Source (Join-Path $warpRoot 'LAUNCHER/warp_launcher.py') list }
    'open' { & $python.Source (Join-Path $warpRoot 'LAUNCHER/warp_launcher.py') open --task $Task --kind $Kind --core $env:IMPERIUM_ROOT }
    'gate' {
        if (-not $Session) { throw '-Session is required for gate.' }
        & $python.Source (Join-Path $warpRoot 'LAUNCHER/warp_launcher.py') gate --session $Session
    }
}
