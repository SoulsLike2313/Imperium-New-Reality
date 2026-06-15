# PC Registration Commands For This Taskpack

Use PC PowerShell from the Owner machine until this Skill exists.

```powershell
$Repo = "E:\IMPERIUM"
$Zip = "$env:USERPROFILE\Downloads\TASKPACK_NEWGEN_ASTRONOMICON_TASKPACK_SKILL_TUI_CONTOUR_ROUTER_AND_VM_LAUNCH_CARD_PC_V0_1.zip"
$TaskId = "TASK-NEWGEN-ASTRONOMICON-TASKPACK-SKILL-TUI-CONTOUR-ROUTER-AND-VM-LAUNCH-CARD-PC-V0_1"

$IntakeReceipt = "$env:TEMP\astronomicon_skill_intake_receipt.json"
$ResolverReceipt = "$env:TEMP\astronomicon_skill_resolver_receipt.json"

if (!(Test-Path $Repo)) { throw "Repo not found: $Repo" }
if (!(Test-Path $Zip)) { throw "Taskpack ZIP not found: $Zip" }

Set-Location $Repo

python IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_taskpack_intake_v0_1.py `
  --repo-root . `
  --zip-path $Zip `
  --receipt-out $IntakeReceipt

Get-Content $IntakeReceipt -Raw

python IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_id_resolver_v0_1.py `
  --repo-root . `
  --task-id $TaskId `
  --receipt-out $ResolverReceipt

Get-Content $ResolverReceipt -Raw

Write-Host ""
Write-Host "============================================================"
Write-Host "IMPERIUM PC TASK LAUNCH CARD"
Write-Host "============================================================"
Write-Host "STEP:"
Write-Host "ASTRONOMICON TASKPACK REGISTRATION SKILL TUI CONTOUR ROUTER AND VM LAUNCH CARD"
Write-Host ""
Write-Host "TASK_ID:"
Write-Host $TaskId
Write-Host ""
Write-Host "CHAT MESSAGE TO SERVITOR:"
Write-Host "start task"
Write-Host "============================================================"
```

After PASS or PASS_WITH_WARNINGS from resolver, tell Servitor:

```text
start task
```
