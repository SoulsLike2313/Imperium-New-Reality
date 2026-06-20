#requires -Version 5
<#
.SYNOPSIS
  IMPERIUM — личный лаунчер имперского TUI.
.DESCRIPTION
  Без аргументов   -> открывает TUI Трона (оркестрация).
  С именем органа -> открывает TUI этого органа напрямую.
.EXAMPLE
  imperium                 # Трон
  imperium MECHANICUS      # орган MECHANICUS
  imperium MECHANICUS -ThronePermit GRANTED
#>
param(
  [Parameter(Position = 0)]
  [string]$Organ,
  [string]$Config,
  [string]$ThronePermit = "DENIED",
  [switch]$Rich,    # принудительно Rich/Textual backend
  [switch]$Curses   # принудительно curses/текстовый fallback
)
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

# --- найти python ---
$py = $null
foreach ($name in @('python', 'python3', 'py')) {
  $c = Get-Command $name -ErrorAction SilentlyContinue
  if ($c) { $py = $c.Source; break }
}
if (-not $py) { Write-Error 'Python не найден в PATH.'; exit 1 }

# --- доступен ли Rich/Textual backend? ---
function Test-Textual {
  try { & $py -c "import textual" 2>$null; return ($LASTEXITCODE -eq 0) }
  catch { return $false }
}

# --- собрать аргументы ---
$argsList = @()
if ($Organ) {
  # орган открываем в curses-TUI (Rich-лаунчер сам умеет проваливаться в органы клавишей d)
  $script = Join-Path $Here 'organ_tui.py'
  $argsList += $Organ.ToUpper()
  $argsList += @('--throne-permit', $ThronePermit)
}
else {
  $useRich = $false
  if ($Curses) { $useRich = $false }
  elseif ($Rich) { $useRich = $true }
  else { $useRich = (Test-Textual) }
  if ($useRich) { $script = Join-Path $Here 'imperium_textual.py' }
  else { $script = Join-Path $Here 'throne_tui.py' }
}
if ($Config) { $argsList += @('--config', $Config) }

# --- UTF-8 для имперской графики ---
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

& $py $script @argsList
exit $LASTEXITCODE
