param(
    [Parameter(ValueFromRemainingArguments = True)]
    [string[]]$ArgsForRunner
)

$Runner = Join-Path $PSScriptRoot "..\TOOLS\inquisition_agent_runner.py"
py -3 $Runner @ArgsForRunner
exit $LASTEXITCODE
