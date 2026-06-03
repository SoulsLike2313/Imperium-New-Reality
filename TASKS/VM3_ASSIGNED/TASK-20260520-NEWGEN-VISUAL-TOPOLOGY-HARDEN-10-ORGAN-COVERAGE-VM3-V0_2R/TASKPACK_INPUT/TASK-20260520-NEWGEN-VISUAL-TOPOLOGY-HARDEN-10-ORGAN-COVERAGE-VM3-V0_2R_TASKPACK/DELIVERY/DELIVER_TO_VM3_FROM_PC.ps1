$ErrorActionPreference = "Stop"

$TaskId = "TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R"
$OldTaskId = "TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2"
$Key = "$env:USERPROFILE\.ssh\imperium_pc_to_vm3_ed25519_20260418"
$Vm = "vboxuser3@127.0.0.1"
$Port = 2225
$ZipObj = Get-ChildItem "$env:USERPROFILE\Downloads" -File | Where-Object { $_.Name -like "$TaskId*.zip" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $ZipObj) { throw "ZIP not found in Downloads for $TaskId" }
$Zip = $ZipObj.FullName

$RemoteRepo = "/home/vboxuser3/IMPERIUM_WORK/Imperium-"
$RemoteTasks = "$RemoteRepo/IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED"
$RemoteTaskRoot = "$RemoteTasks/$TaskId"
$RemoteTaskpackInput = "$RemoteTaskRoot/TASKPACK_INPUT"

scp -P $Port -i $Key "$Zip" "${Vm}:/tmp/${TaskId}_TASKPACK.zip"

ssh -p $Port -i $Key $Vm "set -e
cd '$RemoteRepo'
echo '=== removing old stopped task folder if present ==='
rm -rf '$RemoteTasks/$OldTaskId'
mkdir -p '$RemoteTaskpackInput'
python3 -m zipfile -e '/tmp/${TaskId}_TASKPACK.zip' '$RemoteTaskpackInput'
echo '=== FIRST READ ==='
find '$RemoteTaskpackInput' -name '00_START_HERE_SERVITOR.md' -print
echo '=== START MESSAGE ==='
find '$RemoteTaskpackInput' -name '00_START_MESSAGE_FOR_SERVITOR.txt' -print
echo '=== GIT STATUS ==='
git status --short"
