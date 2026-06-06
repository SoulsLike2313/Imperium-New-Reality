param(
    [Parameter(ValueFromRemainingArguments = True)]
    [string[]]$ArgsForRunner
)

$Runner = Join-Path $PSScriptRoot "..\TOOLS\schola_imperialis_agent_runner.py"
py -3 $Runner @ArgsForRunner
exit $LASTEXITCODE
