param(
  [Parameter(Mandatory=$true)][string]$TaskPackZip,
  [string]$Root = "E:\IMPERIUM_NEW_GENERATION_NEW_REALITY",
  [switch]$Commit,
  [switch]$Push,
  [switch]$Force
)

$ErrorActionPreference = "Stop"
$TaskId = "TASK-20260605-NEWGEN-PC-ADMINISTRATUM-CURRENT-TRUTH-HEAD-CORRECTION-V0_1"
$ExpectedOrigin = "https://github.com/SoulsLike2313/Imperium-New-Reality.git"

function Write-JsonFile([string]$Path, $Object) {
  $Json = $Object | ConvertTo-Json -Depth 30
  $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Json + "`n", $Utf8NoBom)
}

if (!(Test-Path $Root)) { throw "Root not found: $Root" }
Set-Location $Root

$Branch = (git branch --show-current).Trim()
if ($Branch -ne "master") { throw "BLOCK: branch must be master, actual: $Branch" }

$Origin = (git remote get-url origin).Trim()
if ($Origin -ne $ExpectedOrigin) { throw "BLOCK: origin mismatch. Expected $ExpectedOrigin, actual $Origin" }

$Head = (git rev-parse HEAD).Trim()
$StatusBefore = git status --porcelain
if ($StatusBefore -and -not $Force) {
  throw "BLOCK: working tree is dirty before registration. Re-run with -Force only if the dirt is intentional registration work."
}

$StageDir = Join-Path $Root "EXCHANGE\TASK_PACKS\$TaskId"
$TmpDir = Join-Path $Root ".taskpack_import_tmp\$TaskId"
if (Test-Path $TmpDir) { Remove-Item $TmpDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null
Expand-Archive -Path $TaskPackZip -DestinationPath $TmpDir -Force

$PayloadRoot = Join-Path $TmpDir $TaskId
if (!(Test-Path $PayloadRoot)) {
  $PayloadRoot = $TmpDir
}

if (Test-Path $StageDir) {
  if ($Force) { Remove-Item $StageDir -Recurse -Force } else { throw "BLOCK: task pack already staged at $StageDir. Use -Force to replace." }
}
New-Item -ItemType Directory -Force -Path (Split-Path $StageDir) | Out-Null
Copy-Item -Path $PayloadRoot -Destination $StageDir -Recurse -Force

$TaskEssencePath = Join-Path $StageDir "ASTRONOMICON\task_essence_$TaskId.json"
$RoutePacketPath = Join-Path $StageDir "ASTRONOMICON\task_route_packet_$TaskId.json"
$SessionSeedPath = Join-Path $StageDir "ADMINISTRATUM\task_session_card_$TaskId.json"

$TaskEssence = Get-Content $TaskEssencePath -Raw -Encoding UTF8 | ConvertFrom-Json
$RoutePacket = Get-Content $RoutePacketPath -Raw -Encoding UTF8 | ConvertFrom-Json
$SessionCard = Get-Content $SessionSeedPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($TaskEssence.schema_version -ne "astronomicon.task_essence.v0_1") { throw "BLOCK: bad task essence schema_version" }
if ($RoutePacket.schema_version -ne "astronomicon.task_route_packet.v0_1") { throw "BLOCK: bad route packet schema_version" }
if ($TaskEssence.task_id -ne $TaskId -or $RoutePacket.task_id -ne $TaskId) { throw "BLOCK: task_id mismatch" }

$Now = (Get-Date).ToUniversalTime().ToString("o")
$SessionDir = Join-Path $Root "ADMINISTRATUM\REGISTRATION_CARDS\task_sessions"
New-Item -ItemType Directory -Force -Path $SessionDir | Out-Null
$SessionCard.starting_head = $Head
$SessionCard.task_status = "PLANNED"
$SessionCard.registered_at_utc = $Now
$SessionOut = Join-Path $SessionDir "task_session_card_$TaskId.json"
Write-JsonFile $SessionOut $SessionCard

$DraftDir = Join-Path $Root "ASTRONOMICON\DRAFT_TASK_REGISTRY"
New-Item -ItemType Directory -Force -Path $DraftDir | Out-Null
$RegistrationOut = Join-Path $DraftDir "draft_task_registration_$TaskId.json"
$Registration = [ordered]@{
  schema_id = "astronomicon.draft_task_registration.v0_1"
  task_id = $TaskId
  task_status = "REGISTERED"
  registration_owner_organ = "ADMINISTRATUM"
  classification_owner_organ = "ASTRONOMICON"
  execution_owner = "PC_LOCAL_CODEX_SERVITOR"
  starting_head = $Head
  taskpack_stage_path = "EXCHANGE/TASK_PACKS/$TaskId"
  task_essence_path = "EXCHANGE/TASK_PACKS/$TaskId/ASTRONOMICON/task_essence_$TaskId.json"
  route_packet_path = "EXCHANGE/TASK_PACKS/$TaskId/ASTRONOMICON/task_route_packet_$TaskId.json"
  administratum_task_session_card_path = "ADMINISTRATUM/REGISTRATION_CARDS/task_sessions/task_session_card_$TaskId.json"
  registered_at_utc = $Now
  verdict = "REGISTERED_PENDING_EXECUTION"
  not_proven = @(
    "Task is registered, not executed.",
    "No final PASS is claimed by registration."
  )
}
Write-JsonFile $RegistrationOut $Registration

$IndexPath = Join-Path $DraftDir "draft_registry_index.json"
if (Test-Path $IndexPath) {
  $Index = Get-Content $IndexPath -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
  $Index = [ordered]@{ schema_id = "newgen_astronomicon_draft_registry_index_v0_1"; entries = @(); updated_at_utc = $Now }
}
$Existing = @($Index.entries | Where-Object { $_.task_id -eq $TaskId })
if ($Existing.Count -eq 0) {
  $Entry = [ordered]@{
    task_id = $TaskId
    task_status = "REGISTERED"
    registration_path = "ASTRONOMICON/DRAFT_TASK_REGISTRY/draft_task_registration_$TaskId.json"
    taskpack_stage_path = "EXCHANGE/TASK_PACKS/$TaskId"
    registered_at_utc = $Now
  }
  $Index.entries = @($Index.entries) + $Entry
} else {
  foreach ($Entry in $Index.entries) {
    if ($Entry.task_id -eq $TaskId) {
      $Entry.task_status = "REGISTERED"
      $Entry.registration_path = "ASTRONOMICON/DRAFT_TASK_REGISTRY/draft_task_registration_$TaskId.json"
      $Entry.taskpack_stage_path = "EXCHANGE/TASK_PACKS/$TaskId"
      $Entry.registered_at_utc = $Now
    }
  }
}
$Index.updated_at_utc = $Now
Write-JsonFile $IndexPath $Index

$ReportDir = Join-Path $Root "REPORTS\$TaskId\registration"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$TaskFixture = [ordered]@{ examples = @([ordered]@{ example_id = "owner_taskpack_task_essence"; expected_verdict = "PASS"; payload = $TaskEssence }) }
$RouteFixture = [ordered]@{ examples = @([ordered]@{ example_id = "owner_taskpack_route_packet"; expected_verdict = "PASS"; payload = $RoutePacket }) }
$TaskFixturePath = Join-Path $ReportDir "astronomicon_task_essence_fixture_v0_1.json"
$RouteFixturePath = Join-Path $ReportDir "astronomicon_route_packet_fixture_v0_1.json"
Write-JsonFile $TaskFixturePath $TaskFixture
Write-JsonFile $RouteFixturePath $RouteFixture

python "ASTRONOMICON\TOOLS\astronomicon_task_essence_checker_v0_1.py" --fixtures $TaskFixturePath --output (Join-Path $ReportDir "astronomicon_task_essence_checker_report.json")
python "ASTRONOMICON\TOOLS\astronomicon_route_packet_checker_v0_1.py" --fixtures $RouteFixturePath --output (Join-Path $ReportDir "astronomicon_route_packet_checker_report.json")
python "ADMINISTRATUM\TOOLS\administratum_card_checker_v0_1.py" --allow-external-output --output (Join-Path $ReportDir "administratum_card_checker_report.json")

$Closure = [ordered]@{
  schema_id = "administratum.task_registration_closure_receipt.v0_1"
  task_id = $TaskId
  root = $Root
  branch = $Branch
  origin = $Origin
  starting_head = $Head
  staged_taskpack_path = "EXCHANGE/TASK_PACKS/$TaskId"
  administratum_session_card = "ADMINISTRATUM/REGISTRATION_CARDS/task_sessions/task_session_card_$TaskId.json"
  astronomicon_registration = "ASTRONOMICON/DRAFT_TASK_REGISTRY/draft_task_registration_$TaskId.json"
  report_dir = "REPORTS/$TaskId/registration"
  verdict = "REGISTERED_PENDING_EXECUTION"
  created_at_utc = $Now
}
Write-JsonFile (Join-Path $ReportDir "administratum_task_registration_closure_receipt.json") $Closure

if ($Commit) {
  git add "EXCHANGE/TASK_PACKS/$TaskId" "ADMINISTRATUM/REGISTRATION_CARDS/task_sessions/task_session_card_$TaskId.json" "ASTRONOMICON/DRAFT_TASK_REGISTRY/draft_task_registration_$TaskId.json" "ASTRONOMICON/DRAFT_TASK_REGISTRY/draft_registry_index.json" "REPORTS/$TaskId/registration"
  git commit -m "Register $TaskId"
}

if ($Push) {
  if (-not $Commit) { throw "BLOCK: -Push requires -Commit" }
  git push origin master
  $LocalAfter = (git rev-parse HEAD).Trim()
  $RemoteAfter = ((git ls-remote origin refs/heads/master) -split "\s+")[0]
  if ($LocalAfter -ne $RemoteAfter) { throw "BLOCK: local HEAD != remote HEAD after push" }
  Write-Host "REMOTE CLOSURE PASS: $LocalAfter"
}

Write-Host "ADMINISTRATUM REGISTRATION COMPLETE: $TaskId"
Write-Host "Next: run Codex from $Root and execute the registered task."
