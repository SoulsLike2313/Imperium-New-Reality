#requires -Version 5
<#
.SYNOPSIS
  Установка Rich/Textual backend для IMPERIUM (максимальная красота TUI).
.DESCRIPTION
  Ставит textual+rich в тот же Python, что и лаунчер, затем гоняет selftest.
#>
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

$py = $null
foreach ($name in @('python', 'python3', 'py')) {
  $c = Get-Command $name -ErrorAction SilentlyContinue
  if ($c) { $py = $c.Source; break }
}
if (-not $py) { Write-Error 'Python не найден в PATH.'; exit 1 }

Write-Host '== Ставлю textual + rich ==' -ForegroundColor Yellow
& $py -m pip install --upgrade "textual>=0.50" "rich>=13.0"
if ($LASTEXITCODE -ne 0) { Write-Error 'pip install не удался.'; exit 1 }

Write-Host '== selftest ==' -ForegroundColor Yellow
& $py (Join-Path $Here 'imperium_textual.py') --selftest
Write-Host ''
Write-Host 'Готово. Запуск:  imperium   (или: imperium -Rich)' -ForegroundColor Green
exit $LASTEXITCODE
