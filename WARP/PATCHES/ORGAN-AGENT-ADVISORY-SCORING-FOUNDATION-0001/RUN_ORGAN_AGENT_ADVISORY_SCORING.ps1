$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$Validator = Join-Path $RepoRoot "ORGANS\ASTRONOMICON\VALIDATORS\validate_organ_agent_advisory_scoring.py"

Write-Host "== ORGAN-AGENT-ADVISORY-SCORING-FOUNDATION-0001 =="
Write-Host "Repo root: $RepoRoot"
Write-Host "Files to land: $FilesToLand"

if (-not (Test-Path $FilesToLand)) { throw "FILES_TO_LAND not found: $FilesToLand" }

Copy-Item -Path (Join-Path $FilesToLand "*") -Destination $RepoRoot -Recurse -Force

Remove-Item -Recurse -Force "SUPPORT\LAUNCHER\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

python $Validator --repo-root $RepoRoot --apply
if ($LASTEXITCODE -ne 0) { throw "Organ agent advisory scoring validation failed with exit code $LASTEXITCODE" }

Remove-Item -Recurse -Force "SUPPORT\LAUNCHER\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\TOOLS\__pycache__" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "ORGANS\ASTRONOMICON\VALIDATORS\__pycache__" -ErrorAction SilentlyContinue

Write-Host "ORGAN AGENT ADVISORY SCORING PASS"
