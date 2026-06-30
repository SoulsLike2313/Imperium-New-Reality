# PC intake command block

Run from PC PowerShell.

```powershell
$TaskId = "TASK-20260520-SANCTUM-PLAYWRIGHT-TRUTH-BRAIN-STRIKE-PC-V0_1"
$Repo = "E:\IMPERIUM"
$Zip = "$env:USERPROFILE\Downloads\$TaskId.zip"
$Inbox = "E:\IMPERIUM_CONTEXT\LOCAL\ADMINISTRATUM\INBOX\TASKPACKS\$TaskId"

if (-not (Test-Path $Zip)) {
  Write-Host "BLOCKED_TASKPACK_NOT_FOUND: $Zip"
  exit 1
}

Set-Location $Repo

Write-Host "=== PRECHECK ==="
git rev-parse --short HEAD
git log -5 --oneline
git status --short

Remove-Item $Inbox -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "$Inbox\taskpack" | Out-Null

Copy-Item -LiteralPath $Zip -Destination "$Inbox\$TaskId.zip" -Force
Expand-Archive -LiteralPath "$Inbox\$TaskId.zip" -DestinationPath "$Inbox\taskpack" -Force

Get-FileHash -Algorithm SHA256 "$Inbox\$TaskId.zip" |
  ConvertTo-Json -Depth 5 |
  Set-Content -LiteralPath "$Inbox\SHA256SUMS.intake.json" -Encoding UTF8

@{
  schema_version = "PC_ADMINISTRATUM_TASKPACK_INTAKE_RECEIPT_V0_1"
  task_id = $TaskId
  repo_root = $Repo
  taskpack_zip = "$Inbox\$TaskId.zip"
  taskpack_unpacked = "$Inbox\taskpack"
  start_file = "$Inbox\taskpack\START_HERE.md"
  read_sequence = "$Inbox\taskpack\READ_SEQUENCE.json"
  micro_prompt = "$Inbox\taskpack\MICRO_PROMPT_TO_SERVITOR.txt"
  status = "PC_INTAKE_READY_FOR_SERVITOR"
} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath "$Inbox\PC_ADMINISTRATUM_TASKPACK_INTAKE_RECEIPT.json" -Encoding UTF8

Write-Host "PC_ADMINISTRATUM_TASKPACK_INTAKE_READY"
Write-Host "$Inbox\taskpack"
Get-Content "$Inbox\PC_ADMINISTRATUM_TASKPACK_INTAKE_RECEIPT.json"
```

Then give PC Servitor:

```text
Start task.

Taskpack path:
E:\IMPERIUM_CONTEXT\LOCAL\ADMINISTRATUM\INBOX\TASKPACKS\TASK-20260520-SANCTUM-PLAYWRIGHT-TRUTH-BRAIN-STRIKE-PC-V0_1\taskpack

Read START_HERE.md first.
```
