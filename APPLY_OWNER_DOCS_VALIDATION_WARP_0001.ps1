$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
  throw "Run this from repository root."
}

$PatchDir = "WARP\PATCHES\OWNER-DOCS-VALIDATION-WARP-0001"
if (-not (Test-Path $PatchDir)) {
  throw "Patch dir not found after extraction: $PatchDir"
}

Write-Host "Patch present: $PatchDir"
Write-Host "Run validation:"
Write-Host "pwsh WARP/PATCHES/OWNER-DOCS-VALIDATION-WARP-0001/RUN_OWNER_DOCS_VALIDATION.ps1"
