$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"

Write-Host "== GREAT-NINE-PROFILE-VALIDATORS-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

$Organs = @(
  "ASTRONOMICON",
  "ADMINISTRATUM",
  "DOCTRINARIUM",
  "MECHANICUS",
  "INQUISITION",
  "CUSTODES",
  "STRATEGIUM",
  "SCHOLA_IMPERIALIS",
  "OFFICIO_AGENTIS"
)

foreach ($Organ in $Organs) {
  Remove-Item -Recurse -Force "ORGANS\$Organ\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
  $Validator = "ORGANS\$Organ\VALIDATORS\validate_$($Organ.ToLower())_profile.py"
  if (-not (Test-Path $Validator)) { throw "Missing organ profile validator: $Validator" }

  Write-Host ""
  Write-Host "Running $Organ profile validator..."
  python $Validator --repo-root $RepoRoot
  if ($LASTEXITCODE -ne 0) { throw "$Organ profile validator failed with exit code $LASTEXITCODE" }
  Remove-Item -Recurse -Force "ORGANS\$Organ\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Running Throne Great Nine profile audit..."
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
python ORGANS/THRONE/VALIDATORS/validate_great_nine_profile_baseline.py --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { throw "Throne Great Nine profile audit failed with exit code $LASTEXITCODE" }
Remove-Item -Recurse -Force "ORGANS\THRONE\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "GREAT NINE PROFILE VALIDATORS PASS"
