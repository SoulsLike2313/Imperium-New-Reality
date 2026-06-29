$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$Validator = Join-Path $PSScriptRoot "VALIDATORS\validate_owner_foundation_docs.py"

Write-Host "== OWNER-DOCS-VALIDATION-WARP-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Validator: $Validator"

if (-not (Test-Path $Validator)) {
  throw "Validator not found: $Validator"
}

python $Validator --repo-root $RepoRoot
$Code = $LASTEXITCODE

if ($Code -ne 0) {
  throw "Owner docs validation failed with exit code $Code"
}

Write-Host "Validation PASS"
