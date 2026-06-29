$ErrorActionPreference = "Stop"

param(
  [string]$RepoRoot = (Get-Location).Path
)

$SourceOrgans = Join-Path $PSScriptRoot "ORGANS"
if (!(Test-Path $SourceOrgans)) {
  throw "ORGANS payload not found next to this script. Extract the zip first."
}

Write-Host "Applying owner foundation documents into Reality root: $RepoRoot"
Copy-Item -Path $SourceOrgans -Destination $RepoRoot -Recurse -Force
Write-Host "Done. Review and commit after reading the files. Validators are intentionally not included in this direct Reality doc pack."
