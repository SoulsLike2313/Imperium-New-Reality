param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$AstronomiconArgs
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Skill = Join-Path $RepoRoot 'ORGANS\ASTRONOMICON\SKILLS\TASKPACK_REGISTRATION_SKILL\astronomicon_taskpack_registration_skill_v0_1.py'

if (-not (Test-Path -LiteralPath $Skill)) {
  throw "Astronomicon registration skill not found: $Skill"
}

if (-not $AstronomiconArgs -or $AstronomiconArgs.Count -eq 0) {
  $AstronomiconArgs = @('--discovery-smoke')
}

Push-Location $RepoRoot
try {
  & python $Skill @AstronomiconArgs
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
