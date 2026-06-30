# PC launch command for Owner

Use this on PC after downloading this ZIP to Downloads.

```powershell
$ErrorActionPreference = "Stop"

$Repo = "E:\IMPERIUM"
$TaskId = "TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1"
$Zip = Join-Path $env:USERPROFILE "Downloads\TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1_DOSSIER.zip"
$Out = Join-Path $Repo "IMPERIUM_NEW_GENERATION\INBOX\TASKPACKS\$TaskId"

if (!(Test-Path $Zip)) {
  throw "ZIP not found: $Zip"
}

New-Item -ItemType Directory -Force -Path $Out | Out-Null
Expand-Archive -Path $Zip -DestinationPath $Out -Force

Set-Location $Repo
git status --short
git rev-parse HEAD

Write-Host ""
Write-Host "Taskpack extracted to:"
Write-Host $Out
Write-Host ""
Write-Host "Now give Servitor this file first:"
Write-Host (Join-Path $Out "00_START_HERE_SERVITOR.md")
```
