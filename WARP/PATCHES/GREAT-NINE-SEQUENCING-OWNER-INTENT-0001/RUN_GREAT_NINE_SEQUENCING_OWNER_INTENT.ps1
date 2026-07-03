$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\DOCTRINARIUM\VALIDATORS\validate_great_nine_sequencing_owner_intent.py"

Write-Host "== GREAT-NINE-SEQUENCING-OWNER-INTENT-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force
Remove-Item -Recurse -Force "ORGANS\DOCTRINARIUM\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Great Nine sequencing owner intent validator failed with exit code $LASTEXITCODE" }
Remove-Item -Recurse -Force "ORGANS\DOCTRINARIUM\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue
Write-Host "GREAT NINE SEQUENCING OWNER INTENT PASS"
