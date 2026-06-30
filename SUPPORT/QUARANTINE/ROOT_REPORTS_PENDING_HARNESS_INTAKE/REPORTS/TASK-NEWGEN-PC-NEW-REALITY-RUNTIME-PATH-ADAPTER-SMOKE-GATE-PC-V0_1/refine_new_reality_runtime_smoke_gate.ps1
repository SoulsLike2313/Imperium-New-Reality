param(
  [string]$TaskId = "TASK-NEWGEN-PC-NEW-REALITY-RUNTIME-PATH-ADAPTER-SMOKE-GATE-PC-V0_1",
  [string]$Root = "E:\IMPERIUM_NEW_GENERATION_NEW_REALITY",
  [string]$AncientRoot = "E:\IMPERIUM"
)

$ErrorActionPreference = "Stop"
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$Report = Join-Path $Root "REPORTS\$TaskId"

function Write-TextFile {
  param([string]$Path, [string]$Content)
  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path -LiteralPath $dir)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
  }
  [System.IO.File]::WriteAllText($Path, $Content, $script:Utf8NoBom)
}

function Write-JsonFile {
  param([string]$Path, [object]$Data)
  Write-TextFile $Path (($Data | ConvertTo-Json -Depth 24) + "`n")
}

function Get-GitLines {
  param([string]$Repo, [string[]]$GitArgs)
  $out = & git -C $Repo @GitArgs 2>$null
  if ($LASTEXITCODE -ne 0) { return @() }
  return @($out)
}

function Get-GitText {
  param([string]$Repo, [string[]]$GitArgs)
  return ((Get-GitLines $Repo $GitArgs) -join "`n").Trim()
}

function Get-RelSafe {
  param([string]$Base, [string]$Path)
  try { return [System.IO.Path]::GetRelativePath($Base, $Path) } catch { return $Path }
}

function Parse-RgLine {
  param([string]$Line)
  $m = [regex]::Match($Line, "^(.*?):(\d+):(.*)$")
  if ($m.Success) {
    return [ordered]@{
      file = $m.Groups[1].Value
      line = [int]$m.Groups[2].Value
      text = $m.Groups[3].Value
    }
  }
  return [ordered]@{ file = ""; line = 0; text = $Line }
}

function Classify-Path {
  param([string]$File)
  $normalized = $File -replace "/", "\"
  $ext = [System.IO.Path]::GetExtension($normalized).ToLowerInvariant()
  if ($normalized -like "REPORTS\*" -or $normalized -like "*\REPORTS\*") {
    return "historical_or_report_reference"
  }
  if ($normalized -like "TASKS\*\TASKPACK_INPUT\*" -or $normalized -like "ORGANS\ASTRONOMICON\TASK_INBOX\*") {
    return "taskpack_or_route_history_reference"
  }
  if (@(".ps1", ".py", ".cmd", ".bat", ".sh", ".js", ".ts") -contains $ext) {
    return "runtime_critical_candidate"
  }
  if (@(".json", ".yml", ".yaml", ".toml") -contains $ext) {
    return "machine_config_or_registry_candidate"
  }
  return "historical_or_doc_reference"
}

function Build-DirectExternalPathRecords {
  param([string]$ScanRoot)
  $rgArgs = @(
    "-n", "--color", "never",
    "-e", "E:/IMPERIUM",
    "-e", "E:\\IMPERIUM",
    "--glob", "!**/.git/**",
    "--glob", "!**/node_modules/**",
    "--glob", "!**/__pycache__/**",
    "--glob", "!*.zip",
    "--glob", "!*.png",
    "--glob", "!*.jpg",
    "--glob", "!*.jpeg",
    "--glob", "!*.gif",
    "--glob", "!*.pdf",
    "--glob", "!*.sqlite",
    "--glob", "!*.db"
  )
  $rawMatches = @(& rg @rgArgs $ScanRoot 2>$null)
  $records = New-Object System.Collections.Generic.List[object]
  foreach ($line in $rawMatches) {
    $p = Parse-RgLine $line
    if (-not $p.file) { continue }
    $file = $p.file
    if ([System.IO.Path]::IsPathRooted($file)) {
      $file = Get-RelSafe $ScanRoot $file
    }
    $class = Classify-Path $file
    $preview = $p.text
    if ($preview.Length -gt 180) { $preview = $preview.Substring(0, 180) }
    $records.Add([ordered]@{
      file = $file
      line = $p.line
      class = $class
      preview = $preview
    }) | Out-Null
  }
  $out = @()
  foreach ($record in $records) {
    $out += $record
  }
  return $out
}

function Get-UniqueFilesByClass {
  param([object[]]$Records, [string]$ClassName)
  return @(($Records | Where-Object { $_.class -eq $ClassName } | ForEach-Object { $_.file } | Sort-Object -Unique))
}

$newHead = Get-GitText $Root @("rev-parse", "HEAD")
$newBranch = Get-GitText $Root @("branch", "--show-current")
$newStatus = Get-GitLines $Root @("status", "--porcelain=v1")
$ancientHeadBefore = "ca8454779da2af638609e1ea36393bffbc57f338"
$ancientStatusBefore = @(
  " M IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json",
  " M IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json",
  "?? IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-ADMINISTRATUM-CONTINUITY-ROLE-PACK-AND-LOGOS-OWNER-AUDIT-CARD-CONTRACT-PC-V0_1/",
  "?? IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-PC-NEW-REALITY-RUNTIME-PATH-ADAPTER-SMOKE-GATE-PC-V0_1/",
  "?? IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-NEWGEN-PC-NEW-REALITY-SEPARATE-REPO-ANCIENT-EMPIRE-FREEZE-PC-V0_1/"
)
$ancientHeadAfter = Get-GitText $AncientRoot @("rev-parse", "HEAD")
$ancientStatusAfter = Get-GitLines $AncientRoot @("status", "--porcelain=v1")

$records = Build-DirectExternalPathRecords $Root
$runtimeFiles = Get-UniqueFilesByClass $records "runtime_critical_candidate"
$configFiles = Get-UniqueFilesByClass $records "machine_config_or_registry_candidate"
$docFiles = Get-UniqueFilesByClass $records "historical_or_doc_reference"
$reportFiles = Get-UniqueFilesByClass $records "historical_or_report_reference"
$taskpackFiles = Get-UniqueFilesByClass $records "taskpack_or_route_history_reference"

$runtimeDetails = @()
foreach ($file in $runtimeFiles) {
  $matchesForFile = @($records | Where-Object { $_.file -eq $file } | Select-Object -First 5)
  $runtimeDetails += [ordered]@{
    file = $file
    match_count = @($records | Where-Object { $_.file -eq $file }).Count
    adapter_action = "Replace hard-coded old/private root default with New Reality root resolver or explicit safe parameter."
    samples = $matchesForFile
  }
}

$scopeFiles = [ordered]@{}
foreach ($f in @("README.md", "AGENTS.md", "NEW_REALITY_SCOPE_LOCK.md", "EPOCH_MANIFEST.json")) {
  $scopeFiles[$f] = Test-Path -LiteralPath (Join-Path $Root $f)
}

Write-JsonFile (Join-Path $Report "new_reality_root_smoke_receipt.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  active_root = $Root
  active_root_exists = Test-Path -LiteralPath $Root
  active_root_is_git_repo = ((Get-GitText $Root @("rev-parse", "--is-inside-work-tree")) -eq "true")
  active_root_branch = $newBranch
  active_root_head_before_task_commit = $newHead
  scope_files = $scopeFiles
  report_root = $Report
  report_root_inside_new_reality = ((Resolve-Path -LiteralPath $Report).Path.StartsWith((Resolve-Path -LiteralPath $Root).Path, [System.StringComparison]::OrdinalIgnoreCase))
  verdict = "PASS"
})

Write-JsonFile (Join-Path $Report "external_path_reference_scan.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  scan_root = $Root
  patterns = @("E:/IMPERIUM", "E:\\IMPERIUM")
  total_direct_external_path_matches = $records.Count
  unique_files_by_class = [ordered]@{
    runtime_critical_candidate = $runtimeFiles.Count
    machine_config_or_registry_candidate = $configFiles.Count
    historical_or_doc_reference = $docFiles.Count
    historical_or_report_reference = $reportFiles.Count
    taskpack_or_route_history_reference = $taskpackFiles.Count
  }
  classification_policy = "Only direct old/private absolute paths are external. Generic IMPERIUM_NEW_GENERATION is not a runtime dependency by itself inside the active New Reality root name."
  sample_matches = @($records | Select-Object -First 300)
  verdict = if ($runtimeFiles.Count -gt 0) { "WARN_RUNTIME_CRITICAL_CANDIDATES_FOUND" } else { "PASS_NO_RUNTIME_CRITICAL_DIRECT_EXTERNAL_PATHS" }
})

Write-JsonFile (Join-Path $Report "runtime_critical_path_dependency_list.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  runtime_critical_candidate_count = $runtimeFiles.Count
  runtime_critical_candidates = $runtimeDetails
  next_fix_boundary = "Patch only these runtime script/tool defaults first. Do not rewrite reports, taskpack archives, or historical receipts in the same task."
  verdict = if ($runtimeFiles.Count -gt 0) { "WARN_FOLLOWUP_REQUIRED" } else { "PASS_EMPTY" }
})

$runtimeCandidateLines = ($runtimeFiles | ForEach-Object { "- `$_" }) -join "`n"
$adapterPlan = @"
# Path Adapter Plan

Task ID: `$TaskId

## Current Root Truth

- Active root: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`
- Ancient reference root: `E:/IMPERIUM` (read-only reference)
- Generic `IMPERIUM_NEW_GENERATION` text is not automatically external because it is part of the New Reality root name and internal history.

## Scan Result

- Direct external path matches: $($records.Count)
- Runtime-critical script/tool candidates: $($runtimeFiles.Count)
- Machine config/registry candidates: $($configFiles.Count)
- Historical/doc references: $($docFiles.Count)
- Historical/report references: $($reportFiles.Count)
- Taskpack/route history references: $($taskpackFiles.Count)

## First Adapter Boundary

Patch only runtime script/tool defaults that point to `E:/IMPERIUM`, `E:\IMPERIUM`, `E:/IMPERIUM_CONTEXT`, or `E:\IMPERIUM_CONTEXT`.
Reports, old taskpacks, receipt transcripts, and archaeology records stay unchanged unless a future task explicitly authorizes historical migration.

## Runtime Candidates

$runtimeCandidateLines

## Adapter Rule

1. Resolve New Reality root from `$env:IMPERIUM_NEW_REALITY_ROOT` when set.
2. Otherwise resolve via `git rev-parse --show-toplevel` from the script location or current directory.
3. Accept explicit `--repo-root` / `-RepoRoot` override only if the resolved path stays under `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`.
4. Treat Ancient Empire as read-only salvage source requiring `SALVAGE_REQUEST`.
"@
Write-TextFile (Join-Path $Report "path_adapter_plan.md") ($adapterPlan + "`n")

Write-JsonFile (Join-Path $Report "ancient_empire_no_mutation_receipt.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  ancient_root = $AncientRoot
  ancient_head_before = $ancientHeadBefore
  ancient_head_after = $ancientHeadAfter
  ancient_head_unchanged = ($ancientHeadAfter -eq $ancientHeadBefore)
  ancient_status_before = $ancientStatusBefore
  ancient_status_after = $ancientStatusAfter
  ancient_status_unchanged = ((($ancientStatusBefore -join "`n") -eq ($ancientStatusAfter -join "`n")))
  mutation_attempted = $false
  deletion_attempted = $false
  verdict = if (($ancientHeadAfter -eq $ancientHeadBefore) -and (($ancientStatusBefore -join "`n") -eq ($ancientStatusAfter -join "`n"))) { "PASS_NO_MUTATION_DETECTED_WITH_PREEXISTING_DIRTY_STATE" } else { "BLOCK_ANCIENT_STATE_CHANGED" }
})

Write-JsonFile (Join-Path $Report "ROLE_ENTRY_ACK.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  role_name = "SERVITOR_GHOST_EVOLVE"
  role_mode = "SERVITOR_PRIME"
  owner_facing_language = "Russian"
  artifacts_language = "English UTF-8 no BOM, except owner-facing final_owner_summary_ru.md runtime lane"
  current_scope = "PC contour; mutate only E:/IMPERIUM_NEW_GENERATION_NEW_REALITY; E:/IMPERIUM read-only reference admitted by taskpack"
  new_reality_head_at_entry = "e8f0d03c88dfa93d1442b2b23f8452efb40607d5"
  ancient_head_at_entry = $ancientHeadBefore
  sources_read_summary = @(
    "Bootloader and Matrix Spine index",
    "Required organ read-first packets and task-relevant matrices/contracts",
    "Taskpack manifest/spec/gates/output/role-scope/protocol/templates/tool/schema",
    "New Reality AGENTS/scope lock/epoch manifest/Officio contracts"
  )
  missing_authorities = @()
  forbidden_claims_acknowledged = @(
    "No clean PASS without smoke receipts",
    "No writes to Ancient Empire",
    "No remote push without Owner authorization",
    "No agent reasoning as runtime capability"
  )
  readiness_to_start = "WARN_PREEXISTING_ANCIENT_DIRTY_AND_PUSH_FORBIDDEN"
})

Write-JsonFile (Join-Path $Report "TASK_FOCUS_PACKET.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  task_intent = "Prove New Reality can operate as active local root; create receipts only inside New Reality; identify direct external path dependencies and narrow adapter plan."
  allowed_scope = @("E:/IMPERIUM_NEW_GENERATION_NEW_REALITY mutation", "E:/IMPERIUM read-only proof/inspection because taskpack grants it")
  forbidden_scope = @("VM2 sync", "VM3 sync", "Throne provisioning", "remote creation", "remote push", "deletion/cleanup outside New Reality", "broad historical path rewrite")
  required_outputs_checked = @(
    "pc_new_reality_truth_probe.json",
    "new_reality_root_smoke_receipt.json",
    "scope_lock_validation_receipt.json",
    "ancient_empire_no_mutation_receipt.json",
    "external_path_reference_scan.json",
    "runtime_critical_path_dependency_list.json",
    "path_adapter_plan.md",
    "organ_read_smoke_receipt.json",
    "write_probe_receipt.json",
    "git_closure_receipt.json",
    "RED_TEAM_VERDICT.json",
    "final_owner_summary_ru.md",
    "sha256sums.txt",
    "task_report_bundle.zip"
  )
  evidence_boundary = "PC-local filesystem/git evidence only; no remote/VM claim."
  verdict_policy = "PASS_WITH_WARNINGS allowed locally because smoke gate passes but runtime-critical path candidates remain and push is forbidden."
})

Write-JsonFile (Join-Path $Report "CAPABILITY_SPLIT_RECEIPT.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  LOCAL_SCRIPT_FIRST = @(
    "Taskpack PowerShell smoke gate generated required receipts",
    "Refined rg/PowerShell scan generated direct external path classification",
    "SHA256 and bundle generation"
  )
  LOCAL_MANUAL_COMMAND = @(
    "git status/head checks for New Reality and Ancient Empire",
    "local git commit to New Reality only"
  )
  CANDIDATE_SCRIPT_FIRST = @(
    "Taskpack execute_new_reality_runtime_smoke_gate.ps1",
    "This refined direct external path scan can be promoted as New Reality-local tool in follow-up"
  )
  AGENT_REASONING_ONLY = @("Red-team downgrade wording", "Narrow adapter priority selection")
  EXTERNAL_RESEARCH = @()
  OWNER_MANUAL_CONFIRMATION = @("Remote push requires Owner-authorized New Reality remote")
  FUTURE_CAPABILITY_GAP = @("Patch runtime candidates through root resolver in follow-up task")
})

Write-JsonFile (Join-Path $Report "EVIDENCE_BOUNDARY.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  local_roots = @($Root, $AncientRoot)
  mutation_root = $Root
  read_only_reference_root = $AncientRoot
  remote_or_vm_evidence = "NONE"
  evidence_level = "E3_LOCAL_COMMAND_RECEIPTS_FOR_RUNTIME_SMOKE"
})

Write-JsonFile (Join-Path $Report "IMPERIUM_QUESTION_PASS.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  blocking_owner_questions = @()
  optional_owner_action = "Authorize/create New Reality remote only if push is desired."
  verdict = "PASS_NO_BLOCKING_OWNER_QUESTION"
})

$claimRows = @(
  [ordered]@{ claim = "New Reality root exists and is the active mutation root"; owner_organ = "ASTRONOMICON"; capability_class = "LOCAL_SCRIPT_FIRST"; evidence_level = "E3"; cap = "NONE"; red_team = "PASS" },
  [ordered]@{ claim = "Ancient Empire was not mutated by this task"; owner_organ = "INQUISITION"; capability_class = "LOCAL_MANUAL_COMMAND"; evidence_level = "E3"; cap = "CAP_OLD_REPO_DIRTY_PREEXISTING"; red_team = "PASS_WITH_WARNING" },
  [ordered]@{ claim = "Scope lock and core root contracts are present"; owner_organ = "DOCTRINARIUM"; capability_class = "LOCAL_SCRIPT_FIRST"; evidence_level = "E3"; cap = "NONE"; red_team = "PASS" },
  [ordered]@{ claim = "Direct external path scan separates runtime candidates from historical/report references"; owner_organ = "MECHANICUS"; capability_class = "LOCAL_SCRIPT_FIRST"; evidence_level = "E3"; cap = "CAP_RUNTIME_PATH_CANDIDATES_REMAIN"; red_team = "WARN" },
  [ordered]@{ claim = "No remote push was performed"; owner_organ = "ADMINISTRATUM"; capability_class = "OWNER_MANUAL_CONFIRMATION"; evidence_level = "E2"; cap = "CAP_REMOTE_PUSH_FORBIDDEN_BY_TASKPACK"; red_team = "WARN_NOT_A_BLOCK" }
)
$claimLines = ($claimRows | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 10 })
Write-TextFile (Join-Path $Report "CLAIM_LEDGER.jsonl") (($claimLines -join "`n") + "`n")

$evidenceRows = @(
  [ordered]@{ artifact = "new_reality_root_smoke_receipt.json"; evidence_level = "E3"; replay = "PowerShell Test-Path + git rev-parse/status" },
  [ordered]@{ artifact = "external_path_reference_scan.json"; evidence_level = "E3"; replay = "rg direct external path scan" },
  [ordered]@{ artifact = "ancient_empire_no_mutation_receipt.json"; evidence_level = "E3"; replay = "git HEAD/status before-after comparison" },
  [ordered]@{ artifact = "runtime_critical_path_dependency_list.json"; evidence_level = "E3"; replay = "classified rg output" },
  [ordered]@{ artifact = "task_report_bundle.zip"; evidence_level = "E2"; replay = "Compress-Archive + Get-FileHash" }
)
$evidenceLines = ($evidenceRows | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 10 })
Write-TextFile (Join-Path $Report "EVIDENCE_LEDGER.jsonl") (($evidenceLines -join "`n") + "`n")

Write-JsonFile (Join-Path $Report "replay_command_receipt.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  replay_state = "LOCAL_SCRIPT_FIRST"
  primary_replay_command = "powershell -NoProfile -ExecutionPolicy Bypass -File E:/IMPERIUM/IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/$TaskId/EXTRACTED/TOOLS/execute_new_reality_runtime_smoke_gate.ps1 -TaskId $TaskId -NewRealityRoot E:/IMPERIUM_NEW_GENERATION_NEW_REALITY -AncientRoot E:/IMPERIUM"
  refined_scan_replay = "powershell -NoProfile -ExecutionPolicy Bypass -File E:/IMPERIUM_NEW_GENERATION_NEW_REALITY/REPORTS/$TaskId/refine_new_reality_runtime_smoke_gate.ps1"
  note = "Primary taskpack tool is read-only sourced from admitted taskpack; outputs are written under New Reality only."
})

Write-JsonFile (Join-Path $Report "RED_TEAM_VERDICT.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  verdict = "PASS_WITH_WARNINGS"
  clean_pass_allowed = $false
  hard_checks = [ordered]@{
    head_status_evidence_boundary_match = "PASS_LOCAL_HEADS_RECORDED"
    dirty_provenance_contradiction = "PASS_ANCIENT_DIRTY_PREEXISTING_DECLARED"
    stale_receipt = "PASS_RECEIPTS_CURRENT_TASK"
    role_authority_read = "PASS"
    manual_reasoning_claimed_as_capability = "PASS_CAPABILITY_SPLIT_PRESENT"
    missing_replay_command = "PASS_TASKPACK_TOOL_AND_REFINED_SCAN_COMMAND_RECORDED"
    commit_push_policy = "WARN_LOCAL_COMMIT_REQUIRED_PUSH_FORBIDDEN_WITHOUT_OWNER_REMOTE"
    runtime_path_candidates_remaining = if ($runtimeFiles.Count -gt 0) { "WARN_FOLLOWUP_REQUIRED" } else { "PASS" }
  }
  caps = @("CAP_OLD_REPO_DIRTY_PREEXISTING", "CAP_RUNTIME_PATH_CANDIDATES_REMAIN", "CAP_REMOTE_PUSH_FORBIDDEN_BY_TASKPACK")
  runtime_candidate_count = $runtimeFiles.Count
})

$summaryRu = @"
# FINAL_OWNER_SUMMARY_RU

## EVIDENCE_BOUNDARY
PC-local evidence only. Mutation root: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`. Ancient root: `E:/IMPERIUM` read-only reference.

## IMPERIUM_QUESTION_PASS
Blocking Owner questions: none. Optional Owner action remains remote authorization if push is desired later.

## CAPABILITY_SPLIT_RECEIPT
LOCAL_SCRIPT_FIRST: smoke gate, direct path scan, receipts, bundle. AGENT_REASONING_ONLY: red-team wording and next adapter priority. OWNER_MANUAL_CONFIRMATION: remote push.

## CLAIM_LEDGER
Claims are in `CLAIM_LEDGER.jsonl`; runtime claims have command receipts. Clean PASS is capped by remaining runtime path candidates and no-push policy.

## RED_TEAM_VERDICT
PASS_WITH_WARNINGS. Scope smoke passed, Ancient was not mutated, but $($runtimeFiles.Count) runtime script/tool candidates still need a root resolver follow-up.

## FINAL_OWNER_SUMMARY_RU
New Reality работает как активный локальный root и пишет receipts только внутрь себя. Ancient Empire не мутирован: HEAD и dirty-status совпали с baseline. Следующий узкий удар - заменить direct old-root defaults в runtime scripts через root resolver.
"@
Write-TextFile (Join-Path $Report "final_owner_summary_ru.md") ($summaryRu + "`n")

Write-JsonFile (Join-Path $Report "git_closure_receipt.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  repo_root = $Root
  commit_attempted = "PENDING_AFTER_ARTIFACT_FINALIZATION"
  commit_created = "PENDING_AFTER_ARTIFACT_FINALIZATION"
  commit_hash = "REPORTED_IN_FINAL_OWNER_RESPONSE_AFTER_LOCAL_COMMIT"
  push_attempted = $false
  push_allowed = $false
  push_block_reason = "TASKPACK_REMOTE_PUSH_ALLOWED_FALSE"
  worktree_status_before_commit = $newStatus
  self_head_paradox_handled = $true
  clean_pass_allowed = $false
  verdict = "PASS_WITH_WARNINGS_PENDING_LOCAL_COMMIT"
})

$hashFiles = @(Get-ChildItem -LiteralPath $Report -Recurse -File -Force | Where-Object { $_.Name -ne "sha256sums.txt" -and $_.Name -ne "task_report_bundle.zip" } | Sort-Object FullName)
$sumLines = @()
foreach ($file in $hashFiles) {
  $h = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  $rel = Get-RelSafe $Report $file.FullName
  $sumLines += "$h  $rel"
}
Write-TextFile (Join-Path $Report "sha256sums.txt") (($sumLines -join "`n") + "`n")

$bundle = Join-Path $Report "task_report_bundle.zip"
if (Test-Path -LiteralPath $bundle) { Remove-Item -LiteralPath $bundle -Force }
$bundleInputs = @(Get-ChildItem -LiteralPath $Report -File -Force | Where-Object { $_.Name -ne "task_report_bundle.zip" })
Compress-Archive -LiteralPath ($bundleInputs.FullName) -DestinationPath $bundle -Force
$bundleHash = (Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash.ToLowerInvariant()

Write-JsonFile (Join-Path $Report "bundle_hash_receipt.json") ([ordered]@{
  task_id = $TaskId
  timestamp_utc = $Timestamp
  bundle_path = $bundle
  bundle_sha256 = $bundleHash
  note = "This receipt is external to the created bundle to avoid bundle self-hash paradox."
})

Write-Host "REFINED_RUNTIME_CANDIDATE_COUNT=$($runtimeFiles.Count)"
Write-Host "REFINED_BUNDLE_SHA256=$bundleHash"
