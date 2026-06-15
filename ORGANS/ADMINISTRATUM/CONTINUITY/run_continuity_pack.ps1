param(
  [string]$Mode = "h",
  [switch]$Preview,
  [switch]$Smoke
)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Builder = Join-Path $ScriptDir "continuity_pack_builder.py"
if ($Smoke) { python $Builder --smoke; exit $LASTEXITCODE }
if ($Preview) { python $Builder --preview $Mode; exit $LASTEXITCODE }
python $Builder --build $Mode
exit $LASTEXITCODE
