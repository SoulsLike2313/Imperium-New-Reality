$ErrorActionPreference = "Stop"

$TaskId = "TASK-20260520-NEWGEN-MECHANICUS-PANEL-NEURO-FORGE-ANIMATION-VM3-V0_2"
$OldTaskId = "TASK-20260520-NEWGEN-MECHANICUS-PANEL-VISUAL-SLICE-VM3-V0_1"
$Vm = "imperium-vm3"

$ZipObj = Get-ChildItem "$env:USERPROFILE\Downloads" -File |
    Where-Object {
        $_.Name -like "*TASK-20260520-NEWGEN-MECHANICUS-PANEL-NEURO-FORGE-ANIMATION-VM3-V0_2*.zip" -or
        $_.Name -like "*MECHANICUS-PANEL-NEURO-FORGE-ANIMATION-VM3-V0_2*.zip"
    } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $ZipObj) { throw "ZIP not found in Downloads for $TaskId" }

$Zip = $ZipObj.FullName
$LocalDeploy = "$env:TEMP\deploy_vm3_mechanicus_panel_v0_2.sh"

@'
#!/usr/bin/env bash
set -euo pipefail

task="$1"
oldtask="$2"

repo="/home/vboxuser3/IMPERIUM_WORK/Imperium-"
tasks="$repo/IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED"
taskroot="$tasks/$task"
input="$taskroot/TASKPACK_INPUT"
zip="/tmp/${task}_TASKPACK.zip"

cd "$repo"
rm -rf "$tasks/$oldtask"
rm -rf "$taskroot"
mkdir -p "$taskroot"
git status --short | tee "$taskroot/PRE_DELIVERY_GIT_STATUS_BEFORE.txt"
mkdir -p "$input"
python3 -m zipfile -e "$zip" "$input"
echo "=== FIRST READ ==="
find "$input" -name '00_START_HERE_SERVITOR.md' -print
echo "=== START MESSAGE ==="
find "$input" -name '00_START_MESSAGE_FOR_SERVITOR.txt' -print
echo "=== GIT STATUS ==="
git status --short
'@ | Set-Content -Encoding ascii $LocalDeploy

scp "$Zip" "${Vm}:/tmp/${TaskId}_TASKPACK.zip"
scp "$LocalDeploy" "${Vm}:/tmp/deploy_vm3_mechanicus_panel_v0_2.sh"
ssh $Vm "chmod +x /tmp/deploy_vm3_mechanicus_panel_v0_2.sh && /tmp/deploy_vm3_mechanicus_panel_v0_2.sh '$TaskId' '$OldTaskId'"
