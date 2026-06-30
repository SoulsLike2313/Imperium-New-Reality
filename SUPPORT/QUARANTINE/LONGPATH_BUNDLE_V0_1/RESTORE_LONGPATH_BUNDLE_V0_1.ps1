$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$MapPath = Join-Path $PSScriptRoot "LONGPATH_BUNDLE_MAP_V0_1.json"

if (-not (Test-Path $MapPath)) {
  throw "Bundle map not found: $MapPath"
}

$Map = Get-Content $MapPath -Raw | ConvertFrom-Json

foreach ($Entry in $Map.entries) {
  $Source = Join-Path $RepoRoot $Entry.source_rel
  $Bundle = Join-Path $RepoRoot $Entry.bundle_rel
  if (-not (Test-Path $Bundle)) {
    throw "Missing bundle blob: $($Entry.bundle_rel)"
  }
  New-Item -ItemType Directory -Force -Path (Split-Path $Source) | Out-Null
  Copy-Item -LiteralPath $Bundle -Destination $Source -Force
}

Write-Host "Longpath bundle restored from map: $MapPath"
