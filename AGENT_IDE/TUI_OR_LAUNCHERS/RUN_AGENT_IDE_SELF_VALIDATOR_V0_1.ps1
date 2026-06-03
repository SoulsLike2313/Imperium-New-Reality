$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptRoot "..\..\..")).Path
Set-Location $repoRoot
python "IMPERIUM_NEW_GENERATION/AGENT_IDE/SELF_VALIDATOR/agent_ide_self_validator_v0_2.py" @args
