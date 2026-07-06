$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$FilesToLand = Join-Path $PSScriptRoot "FILES_TO_LAND"
$PatchId = "IMPERIUM-APP-ASTRONOMICON-TERMINAL-FIRST-WORKFLOW-0001"

function Copy-LandFiles {
  param([string]$SourceRoot, [string]$DestRoot)
  Get-ChildItem -Path $SourceRoot -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($SourceRoot.Length).TrimStart('\','/')
    $dest = Join-Path $DestRoot $rel
    New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
    Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
  }
}

$pwshVersion = $PSVersionTable.PSVersion.ToString()
if ($pwshVersion -ne "7.6.2") { Write-Host "IMPERIUM SHELL: pwsh $pwshVersion (expected 7.6.2)" -ForegroundColor Yellow } else { Write-Host "IMPERIUM SHELL: pwsh 7.6.2 OK" -ForegroundColor Green }

Copy-LandFiles -SourceRoot $FilesToLand -DestRoot $RepoRoot
Set-Location $RepoRoot

python "SUPPORT/APP_TAURI/tests/validate_astronomicon_terminal_first_workflow.py" --repo-root . --apply
if ($LASTEXITCODE -ne 0) { throw "$PatchId failed with exit code $LASTEXITCODE" }
