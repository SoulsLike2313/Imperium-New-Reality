$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\INQUISITION\VALIDATORS\validate_red_blue_team_tools_skills_foundation.py"

Write-Host "== RED-BLUE-TEAM-TOOLS-AND-SKILLS-FOUNDATION-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "ORGANS\INQUISITION\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\INQUISITION\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Red/Blue team tools and skills foundation validation failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "ORGANS\INQUISITION\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\INQUISITION\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "RED BLUE TEAM TOOLS AND SKILLS FOUNDATION PASS"
