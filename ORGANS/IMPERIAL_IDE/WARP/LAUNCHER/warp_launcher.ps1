<#
.SYNOPSIS
    WARP ZONE launcher (V0.1) — открывает горячую зону разработки.
.DESCRIPTION
    Два пути входа в WARP:
      -Auto   : вызывается IDE автоматически, когда стартует задача
      (без -Auto) : ручной запуск по кнопке WARP в IDE
    Ядро не трогается: всё пишется в WARP/runtime/<session>/.
.EXAMPLE
    pwsh ./warp_launcher.ps1 -Task "build dashboard" -Kind THIRD_PARTY
    pwsh ./warp_launcher.ps1 -Task "patch astronomicon" -Kind CORE_CHANGE -Auto -Core 'E:\IMPERIUM_NEW_GENERATION_NEW_REALITY'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Task,
    [ValidateSet('CORE_CHANGE', 'IMPERIUM_FORCE', 'THIRD_PARTY')]
    [string]$Kind = 'THIRD_PARTY',
    [switch]$Auto,
    [string]$Core = $env:IMPERIUM_ROOT
)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot

$python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $python) { $python = (Get-Command python3 -ErrorAction SilentlyContinue) }
if (-not $python) { Write-Error 'Python 3.10+ требуется в PATH.'; exit 1 }

Write-Host ''
Write-Host '  >>> ENTERING WARP ZONE <<<' -ForegroundColor Magenta
Write-Host "      task = $Task" -ForegroundColor Gray
Write-Host "      kind = $Kind   trigger = $([bool]$Auto ? 'auto' : 'manual')   core = $Core" -ForegroundColor DarkGray
Write-Host ''

$args = @('open', '--task', $Task, '--kind', $Kind)
if ($Auto) { $args += '--auto' }
if ($Core) { $args += @('--core', $Core) }

& $python.Source (Join-Path $here 'warp_launcher.py') @args
