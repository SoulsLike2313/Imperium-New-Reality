$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptRoot "..\\..\\..")).Path
Set-Location $repoRoot
python "IMPERIUM_NEW_GENERATION/AGENT_IDE/APP/agent_ide_app_v0_1.py" @args
