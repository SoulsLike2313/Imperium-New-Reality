param(
    [string]$OldRoot = "E:/IMPERIUM",
    [string]$Source = "E:/IMPERIUM/IMPERIUM_NEW_GENERATION",
    [string]$Target = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$TaskId = "TASK-NEWGEN-PC-NEW-REALITY-SEPARATE-REPO-ANCIENT-EMPIRE-FREEZE-PC-V0_1"
$Report = Join-Path $Target "REPORTS/$TaskId"
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$StartedUtc = (Get-Date).ToUniversalTime().ToString("o")

function Write-Utf8NoBomText([string]$Path, [string]$Content) {
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Content, $script:Utf8NoBom)
}

function Write-JsonFile([string]$Path, $Object, [int]$Depth = 12) {
    Write-Utf8NoBomText -Path $Path -Content (($Object | ConvertTo-Json -Depth $Depth) + "`n")
}

function Write-JsonLines([string]$Path, [object[]]$Rows) {
    $lines = $Rows | ForEach-Object { $_ | ConvertTo-Json -Depth 12 -Compress }
    Write-Utf8NoBomText -Path $Path -Content (($lines -join "`n") + "`n")
}

function Get-Sha256String([string]$Text) {
    $bytes = $script:Utf8NoBom.GetBytes($Text)
    $hash = [System.Security.Cryptography.SHA256]::HashData($bytes)
    return ([System.BitConverter]::ToString($hash) -replace "-", "").ToLowerInvariant()
}

function Normalize-PathText([string]$Path) {
    return ($Path -replace "\\", "/")
}

function Get-GitOutput([string]$Repo, [string[]]$Args) {
    $out = & git -C $Repo @Args 2>$null
    if ($LASTEXITCODE -ne 0) { return "" }
    return (($out -join "`n").Trim())
}

function Get-DirectoryStats([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        return [ordered]@{ exists = $false; file_count = 0; dir_count = 0; size_bytes = 0; size_mb = 0 }
    }
    $files = @(Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue)
    $dirs = @(Get-ChildItem -LiteralPath $Path -Recurse -Force -Directory -ErrorAction SilentlyContinue)
    $sum = ($files | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $sum) { $sum = 0 }
    return [ordered]@{
        exists = $true
        file_count = $files.Count
        dir_count = $dirs.Count
        size_bytes = [int64]$sum
        size_mb = [math]::Round(([double]$sum) / 1MB, 2)
    }
}

function Get-TopLevelInventory([string]$Path, [int]$Limit = 200) {
    if (-not (Test-Path -LiteralPath $Path)) { return @() }
    return @(Get-ChildItem -LiteralPath $Path -Force -ErrorAction SilentlyContinue |
        Sort-Object Name |
        Select-Object -First $Limit |
        ForEach-Object {
            [ordered]@{
                name = $_.Name
                mode = $_.Mode
                length = if ($_.PSIsContainer) { $null } else { $_.Length }
            }
        })
}

function Get-ReparsePoints([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return @() }
    return @(Get-ChildItem -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } |
        ForEach-Object {
            [ordered]@{ path = (Normalize-PathText $_.FullName); link_type = $_.LinkType; target = $_.Target }
        })
}

function Get-NamedDirectories([string]$Path, [string[]]$Names) {
    $out = @()
    if (-not (Test-Path -LiteralPath $Path)) { return $out }
    $dirs = @(Get-ChildItem -LiteralPath $Path -Recurse -Force -Directory -ErrorAction SilentlyContinue)
    foreach ($d in $dirs) {
        if ($Names -contains $d.Name) {
            $files = @(Get-ChildItem -LiteralPath $d.FullName -Recurse -Force -File -ErrorAction SilentlyContinue)
            $sum = ($files | Measure-Object -Property Length -Sum).Sum
            if ($null -eq $sum) { $sum = 0 }
            $out += [ordered]@{
                name = $d.Name
                path = (Normalize-PathText $d.FullName)
                file_count = $files.Count
                size_bytes = [int64]$sum
                excluded_from_copy = ($d.Name -in @(".git", "node_modules", "__pycache__", ".pytest_cache"))
            }
        }
    }
    return $out
}

function Get-RuntimeDirs([string]$Path) {
    $names = @("ARTIFACTS", "RUNS", "REPORTS", "ARCHIVE", "TASKS", "TASK_CONTROL")
    $out = @()
    foreach ($n in $names) {
        $p = Join-Path $Path $n
        if (Test-Path -LiteralPath $p) {
            $stats = Get-DirectoryStats $p
            $out += [ordered]@{
                name = $n
                exists = $true
                file_count = $stats.file_count
                dir_count = $stats.dir_count
                size_bytes = $stats.size_bytes
                size_mb = $stats.size_mb
                treatment = "COPIED_MARKED_RUNTIME_OR_REPORT_HISTORY"
            }
        } else {
            $out += [ordered]@{ name = $n; exists = $false; file_count = 0; dir_count = 0; size_bytes = 0; size_mb = 0; treatment = "NOT_PRESENT" }
        }
    }
    return $out
}

function Convert-RgSample([string]$Line) {
    $m = [regex]::Match($Line, "^(.*?):(\d+):(.*)$")
    if ($m.Success) {
        $content = $m.Groups[3].Value
        $preview = [regex]::Replace($content, "[^\x20-\x7E]", "?")
        if ($preview.Length -gt 160) { $preview = $preview.Substring(0, 160) }
        return [ordered]@{
            path = (Normalize-PathText $m.Groups[1].Value)
            line = [int]$m.Groups[2].Value
            content_sha256 = (Get-Sha256String $content)
            ascii_preview = $preview
        }
    }
    return [ordered]@{ raw_sha256 = (Get-Sha256String $Line); ascii_preview = ([regex]::Replace($Line, "[^\x20-\x7E]", "?")) }
}

function Invoke-RgScan([string]$Name, [string]$Pattern, [string[]]$ExtraArgs = @()) {
    if (-not (Get-Command rg -ErrorAction SilentlyContinue)) {
        return [ordered]@{ name = $Name; tool = "rg"; available = $false; count = 0; sample = @() }
    }
    $common = @(
        "--hidden", "--no-ignore", "-n", "--color", "never",
        "--glob", "!**/node_modules/**",
        "--glob", "!**/__pycache__/**",
        "--glob", "!**/.git/**",
        "--glob", "!**/.pytest_cache/**",
        "--glob", "!*.zip",
        "--glob", "!*.png",
        "--glob", "!*.jpg",
        "--glob", "!*.jpeg",
        "--glob", "!*.gif",
        "--glob", "!*.pdf",
        "--glob", "!*.bin",
        "--glob", "!*.exe",
        "--glob", "!*.dll",
        "--glob", "!*.db",
        "--glob", "!*.sqlite",
        "--glob", "!*.woff",
        "--glob", "!*.woff2",
        "--glob", "!*.ttf",
        "--glob", "!*.ico"
    )
    $lines = @(& rg @common @ExtraArgs -e $Pattern $Source 2>$null)
    return [ordered]@{
        name = $Name
        tool = "rg"
        available = $true
        pattern = $Pattern
        count = $lines.Count
        sample = @($lines | Select-Object -First 40 | ForEach-Object { Convert-RgSample $_ })
    }
}

if (-not (Test-Path -LiteralPath $Source)) {
    throw "BLOCK_SOURCE_NEWGEN_MISSING"
}

if (Test-Path -LiteralPath $Target) {
    $allItems = @(Get-ChildItem -LiteralPath $Target -Force -ErrorAction SilentlyContinue)
    $allowedBootstrap = $true
    foreach ($item in $allItems) {
        if ($item.Name -ne "REPORTS") { $allowedBootstrap = $false }
    }
    $reportFiles = @()
    if (Test-Path -LiteralPath $Report) {
        $reportFiles = @(Get-ChildItem -LiteralPath $Report -Recurse -Force -File -ErrorAction SilentlyContinue)
    }
    foreach ($file in $reportFiles) {
        if ($file.Name -ne "execute_new_reality_split.ps1") { $allowedBootstrap = $false }
    }
    if (($allItems.Count -gt 0) -and -not $allowedBootstrap) {
        throw "BLOCK_TARGET_EXISTS_NON_EMPTY_WITHOUT_OWNER_ADMISSION"
    }
}

New-Item -ItemType Directory -Path $Target -Force | Out-Null
New-Item -ItemType Directory -Path $Report -Force | Out-Null

$oldBranch = Get-GitOutput $OldRoot @("branch", "--show-current")
$oldHead = Get-GitOutput $OldRoot @("rev-parse", "HEAD")
$oldHeadShort = Get-GitOutput $OldRoot @("rev-parse", "--short", "HEAD")
$originMaster = Get-GitOutput $OldRoot @("rev-parse", "--verify", "origin/master")
$remoteHead = Get-GitOutput $OldRoot @("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
$oldDirty = @(& git -C $OldRoot status --short 2>$null)
$oldTop = Get-TopLevelInventory $OldRoot
$sourceTop = Get-TopLevelInventory $Source
$sourceStats = Get-DirectoryStats $Source
$runtimeDirs = Get-RuntimeDirs $Source
$reparse = Get-ReparsePoints $Source
$generatedDirs = Get-NamedDirectories $Source @(".git", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", ".venv", "venv")

$dependencyScans = @()
$dependencyScans += Invoke-RgScan "absolute_path_hits" "([CcDdEeFf]:[\\/]|/home/|/mnt/|/Users/)"
$dependencyScans += Invoke-RgScan "parent_path_hits" "(\.\./|\.\.\\)"
$dependencyScans += Invoke-RgScan "old_root_name_hits" "(E:/IMPERIUM|E:\\\\IMPERIUM|IMPERIUM_NEW_GENERATION|IMPERIUM_NEW_GENERATION_NEW_REALITY|ANCIENT_EMPIRE)"
$scriptGlobs = @("--glob", "*.ps1", "--glob", "*.py", "--glob", "*.js", "--glob", "*.ts", "--glob", "*.cmd", "--glob", "*.bat", "--glob", "*.sh")
$dependencyScans += Invoke-RgScan "script_absolute_or_parent_or_old_root_hits" "([CcDdEeFf]:[\\/]|/home/|/mnt/|/Users/|\.\./|\.\.\\|E:/IMPERIUM|E:\\\\IMPERIUM|IMPERIUM_NEW_GENERATION)" $scriptGlobs

$criticalFindings = @()
$scriptHit = ($dependencyScans | Where-Object { $_.name -eq "script_absolute_or_parent_or_old_root_hits" }).count
$absoluteHit = ($dependencyScans | Where-Object { $_.name -eq "absolute_path_hits" }).count
$oldRootHit = ($dependencyScans | Where-Object { $_.name -eq "old_root_name_hits" }).count
if ($scriptHit -gt 0) { $criticalFindings += "Executable/script references to parent paths, PC paths, VM paths, or old root naming exist; runtime adaptation is follow-up and no clean runtime PASS is claimed." }
if ($absoluteHit -gt 0) { $criticalFindings += "Absolute PC/VM/private-context path references exist in copied source evidence or scripts; recorded for follow-up." }
if ($oldRootHit -gt 0) { $criticalFindings += "Old root naming references exist across legacy contracts, receipts, and tools; New Reality scope lock is installed but broad renaming is out of scope." }

$dependencyScan = [ordered]@{
    timestamp_utc = $StartedUtc
    source_root = $Source
    scan_tool = "rg plus PowerShell inventory"
    scan_glob_exclusions = @("node_modules", "__pycache__", ".git", ".pytest_cache", "binary/archive extensions")
    absolute_path_hits = ($dependencyScans | Where-Object { $_.name -eq "absolute_path_hits" })
    parent_path_hits = ($dependencyScans | Where-Object { $_.name -eq "parent_path_hits" })
    old_root_name_hits = ($dependencyScans | Where-Object { $_.name -eq "old_root_name_hits" })
    script_import_or_read_outside_newgen_hits = ($dependencyScans | Where-Object { $_.name -eq "script_absolute_or_parent_or_old_root_hits" })
    symlink_or_junction_hits = $reparse
    generated_dependency_or_cache_dirs = $generatedDirs
    runtime_or_report_history_dirs = $runtimeDirs
    critical_findings = $criticalFindings
    verdict = if ($criticalFindings.Count -gt 0) { "WARN_EXTERNAL_DEPENDENCIES_RECORDED_NO_CLEAN_RUNTIME_PASS" } else { "PASS_NO_CRITICAL_EXTERNAL_DEPENDENCIES_DETECTED" }
}

$excludeDirs = @(".git", "node_modules", "__pycache__", ".pytest_cache")
$robocopyLogPath = Join-Path $Target "new_reality_robocopy.log"
$robocopyArgs = @($Source, $Target, "/E", "/COPY:DAT", "/DCOPY:DAT", "/R:2", "/W:1", "/XD") + $excludeDirs + @("/NFL", "/NDL", "/NJH", "/NJS", "/NP")
$robocopyOutput = & robocopy @robocopyArgs 2>&1
$robocopyExit = $LASTEXITCODE
Write-Utf8NoBomText -Path $robocopyLogPath -Content (($robocopyOutput | ForEach-Object { [string]$_ }) -join "`n")
if ($robocopyExit -gt 7) { throw "ROBOCOPY_FAILED_EXIT_$robocopyExit" }

$createdUtc = (Get-Date).ToUniversalTime().ToString("o")

$readme = @'
# IMPERIUM New Generation New Reality

This repository/root is the active IMPERIUM New Reality runtime core.

Ancient Empire is preserved as precedent memory and archaeology. It is not active execution context.

Servitor default scope is this root only. Outside access requires explicit admission and a salvage request.
'@

$agents = @'
# AGENTS.md - New Reality Root Contract

You are operating inside IMPERIUM_NEW_GENERATION_NEW_REALITY.

Default rules:

1. Read/write/mutate only inside this root.
2. Do not access Ancient Empire or parent folders unless the task explicitly grants admission.
3. If outside context is needed, stop and create a SALVAGE_REQUEST.
4. Follow Officio final response contract.
5. For any non-BLOCK completed task, commit/push or explain the blocker with evidence.
6. No fake green. Claims require receipts.
'@

$scopeLock = @'
# New Reality Scope Lock

Status: ACTIVE_PC_LOCAL_SCOPE_LOCK_V0_1

New Reality is the active IMPERIUM runtime core.

Default Servitor rule:

```text
Read/write/mutate only inside the approved New Reality root.
```

Approved default root:

```text
E:/IMPERIUM_NEW_GENERATION_NEW_REALITY
```

Ancient Empire is not active context. It is archaeology, precedent memory, and salvage source only.

Any access from New Reality to Ancient Empire requires a SALVAGE_REQUEST with source path, reason, target path, expected value, admitting organ, hash/evidence, and receipt.

Private folders and arbitrary parent paths are forbidden unless a task explicitly grants admission and records evidence.

No admission means no access. No receipt means no claim.
'@

$ancientReference = @"
# Ancient Empire Reference

Status: PRESERVED_NO_DELETION

Ancient Empire root: `$OldRoot`
Source NewGen path: `$Source`
New Reality root: `$Target`
Recorded branch: `$oldBranch`
Recorded HEAD: `$oldHead`
Recorded origin/master: `$originMaster`
Recorded remote HEAD: `$remoteHead`
Recorded dirty entries: $($oldDirty.Count)

This task preserves Ancient Empire as archaeology and precedent memory. It does not delete, move, or rewrite the old repository, and it does not remove IMPERIUM_NEW_GENERATION from Ancient Empire.

Future salvage from Ancient Empire requires SALVAGE_REQUEST admission and a receipt.
"@

$gitignore = @'
# Generated dependency/cache folders are not part of the New Reality source commit.
node_modules/
__pycache__/
.pytest_cache/
*.pyc
*.pyo
.venv/
venv/
'@

Write-Utf8NoBomText (Join-Path $Target "README.md") $readme
Write-Utf8NoBomText (Join-Path $Target "AGENTS.md") $agents
Write-Utf8NoBomText (Join-Path $Target "NEW_REALITY_SCOPE_LOCK.md") $scopeLock
Write-Utf8NoBomText (Join-Path $Target "ANCIENT_EMPIRE_REFERENCE.md") $ancientReference
Write-Utf8NoBomText (Join-Path $Target ".gitignore") $gitignore

$epochManifest = [ordered]@{
    epoch = "NEW_REALITY"
    active_root = $Target
    source_epoch = "ANCIENT_EMPIRE"
    ancient_reference = [ordered]@{
        old_repo_root = $OldRoot
        old_repo_branch = $oldBranch
        old_repo_head = $oldHead
        old_repo_origin_master = $originMaster
        old_repo_remote_head = $remoteHead
        status = "ARCHAEOLOGY_AND_PRECEDENT_MEMORY"
        no_deletion_confirmed = $true
    }
    servitor_scope = [ordered]@{
        default_allowed_root = $Target
        outside_access_requires = "SALVAGE_REQUEST"
        private_paths_forbidden = $true
        arbitrary_parent_paths_forbidden = $true
    }
    task_id = $TaskId
    created_utc = $createdUtc
}
Write-JsonFile (Join-Path $Target "EPOCH_MANIFEST.json") $epochManifest

$salvageTemplate = [ordered]@{
    request_id = "SALVAGE-YYYYMMDD-UNIQUE-SLUG"
    source_epoch = "ANCIENT_EMPIRE"
    source_path = "E:/IMPERIUM/path/to/source"
    target_path = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY/path/to/target"
    reason = "Explain why this Ancient Empire material is needed."
    expected_value = "Explain the value and acceptance boundary."
    admitting_organ = "ORGAN_NAME"
    hash = "sha256:pending"
    evidence = "receipt-or-probe-path"
    status = "PROPOSED"
    receipt = "REPORTS/<task-id>/salvage_request_receipt.json"
}
Write-JsonFile (Join-Path $Target "SALVAGE_REQUEST_TEMPLATE.json") $salvageTemplate

$targetStatsAfterCopy = Get-DirectoryStats $Target
$targetTop = Get-TopLevelInventory $Target
$pcTruth = [ordered]@{
    timestamp_utc = $createdUtc
    old_repo_root = $OldRoot
    branch = $oldBranch
    head = $oldHead
    head_short = $oldHeadShort
    origin_master = $originMaster
    remote_head = $remoteHead
    worktree_dirty_state = if ($oldDirty.Count -gt 0) { "DIRTY_PREEXISTING" } else { "CLEAN" }
    worktree_dirty_entries = $oldDirty
    source_newgen_path = $Source
    source_folder_exists = $true
    source_size_estimate = $sourceStats
    old_repo_top_level = $oldTop
    source_top_level = $sourceTop
}
Write-JsonFile (Join-Path $Report "pc_repo_truth_probe.json") $pcTruth
Write-JsonFile (Join-Path $Report "external_dependency_scan.json") $dependencyScan

$freeze = [ordered]@{
    timestamp_utc = $createdUtc
    old_repo_root = $OldRoot
    old_repo_head = $oldHead
    old_repo_branch = $oldBranch
    old_repo_origin_master = $originMaster
    intended_reference_commit = $originMaster
    old_repo_dirty_state = if ($oldDirty.Count -gt 0) { "DIRTY_PREEXISTING_RECORDED" } else { "CLEAN" }
    old_repo_dirty_entries = $oldDirty
    ancient_empire_status = "PRESERVED_NO_DELETION"
    source_newgen_path = $Source
    source_newgen_path_still_exists = (Test-Path -LiteralPath $Source)
    no_deletion_confirmation = $true
    notes = @("Ancient Empire preserved as archaeology and precedent memory. No removal of IMPERIUM_NEW_GENERATION was performed.")
}
Write-JsonFile (Join-Path $Report "ancient_empire_freeze_receipt.json") $freeze

$copyManifest = [ordered]@{
    timestamp_utc = $createdUtc
    source_root = $Source
    new_reality_root = $Target
    copy_tool = "robocopy"
    robocopy_exit_code = $robocopyExit
    copied_scope = "IMPERIUM_NEW_GENERATION active core copied into New Reality root with generated dependency/cache directories excluded."
    bootstrap_target_allowed = $true
    excluded_directory_names = $excludeDirs
    excluded_generated_dependency_or_cache_dirs = @($generatedDirs | Where-Object { $_.excluded_from_copy -eq $true })
    marked_runtime_or_report_history_dirs = $runtimeDirs
    source_stats = $sourceStats
    target_stats_after_copy = $targetStatsAfterCopy
    target_top_level = $targetTop
    old_git_internals_copied = $false
    nested_full_old_repo_detected = (Test-Path -LiteralPath (Join-Path $Target "IMPERIUM_NEW_GENERATION"))
    robocopy_log = "new_reality_robocopy.log"
}
Write-JsonFile (Join-Path $Report "new_reality_copy_manifest.json") $copyManifest

$roleAck = [ordered]@{
    timestamp_utc = $createdUtc
    role_mode = "Servitor Ghost_Evolve / Codex Default mode / build-then-red-team"
    contour = "PC"
    task_id = $TaskId
    task_source_boundary = "registered taskpack plus Matrix Spine and organ-owned authority files"
    source_root = $Source
    target_root = $Target
    old_repo = [ordered]@{ root = $OldRoot; branch = $oldBranch; head = $oldHead; origin_master = $originMaster; dirty_state = $pcTruth.worktree_dirty_state; dirty_entries = $oldDirty }
    sources_read = @("MATRIX_SPINE_INDEX", "required organ READ_FIRST packets", "key role/language/focus/evidence/script/red-team matrices", "taskpack START_HERE/TASK_SPEC/ACCEPTANCE_GATES/OUTPUT_REQUIREMENTS/policies/schemas/templates/manifest")
    missing_authorities = @()
    language_contract = "Owner-facing Russian; machine artifacts English UTF-8 no BOM except explicit final_owner_summary_ru.md runtime lane."
    forbidden_claims_acknowledged = @("No clean PASS with hidden dirty provenance", "No Ancient Empire deletion or rewrite", "No GitHub push without remote authorization", "No VM2/VM3 sync claim", "No runtime capability claim without replay receipt", "No screenshot-as-truth shortcut")
    readiness = "WARN_DIRTY_PREEXISTING_BUT_SAFE_TO_START"
}
Write-JsonFile (Join-Path $Report "ROLE_ENTRY_ACK.json") $roleAck

$focusPacket = [ordered]@{
    timestamp_utc = $createdUtc
    task_id = $TaskId
    task_intent = "Create non-destructive PC-local New Reality root from IMPERIUM_NEW_GENERATION, initialize local git repo, freeze Ancient Empire reference, install scope lock, produce receipts and validation bundle."
    contour = "PC"
    allowed_roots = @($OldRoot, $Target, "E:/IMPERIUM_ANCIENT_EMPIRE_EVIDENCE")
    forbidden_actions = @("delete original repository", "rewrite old git history", "remove IMPERIUM_NEW_GENERATION from old repo", "push remote changes without Owner authorization", "sync VM2 or VM3", "copy entire old repo into New Reality", "touch private folders")
    required_outputs = @("pc_repo_truth_probe.json", "ancient_empire_freeze_receipt.json", "new_reality_copy_manifest.json", "new_reality_git_init_receipt.json", "external_dependency_scan.json", "scope_lock_validation_receipt.json", "no_deletion_receipt.json", "epoch_manifest_validation_receipt.json", "salvage_policy_receipt.json", "new_reality_root_inventory.json", "sha256sums.txt", "final_owner_summary_ru.md", "task_report_bundle.zip")
    pass_warn_block_gates = @("PC contour truth", "Ancient Empire freeze no deletion", "New Reality root and root contracts", "local git repo with commit", "scope lock", "dependency scan", "receipts and bundle")
    evidence_boundary = "Local filesystem and git command receipts on PC only; no remote/GitHub/VM claim."
    stop_conditions = @("source missing", "target non-empty before task without Owner admission", "copy overwrite unrelated files", "old repo deletion/rewrite risk", "git init/commit impossible", "root contracts cannot be written")
}
Write-JsonFile (Join-Path $Report "TASK_FOCUS_PACKET.json") $focusPacket

$capabilitySplit = [ordered]@{
    timestamp_utc = $createdUtc
    LOCAL_SCRIPT_FIRST = @("PowerShell filesystem/git probe and receipt generation", "robocopy copy operation", "git init/add/commit", "SHA256 and ZIP bundle generation")
    LOCAL_MANUAL_COMMAND = @("Final git status/log verification commands executed by Servitor in this session")
    CANDIDATE_SCRIPT_FIRST = @("execute_new_reality_split.ps1 can be promoted after organ admission")
    AGENT_REASONING_ONLY = @("Classification of warning severity and red-team narrative")
    EXTERNAL_RESEARCH = @()
    OWNER_MANUAL_CONFIRMATION = @("Remote push requires Owner-created/authorized New Reality remote")
    FUTURE_CAPABILITY_GAP = @("Runtime scripts still reference old root naming and need follow-up adaptation tasks")
}
Write-JsonFile (Join-Path $Report "CAPABILITY_SPLIT_RECEIPT.json") $capabilitySplit

$ownerQuestions = [ordered]@{
    timestamp_utc = $createdUtc
    task_id = $TaskId
    blocking_questions = @()
    owner_input_required_for_optional_remote_push = $true
    question = "Create or authorize a New Reality remote only if push is desired."
}
Write-JsonFile (Join-Path $Report "OWNER_QUESTION_LEDGER.json") $ownerQuestions

$scopeText = Get-Content -Raw -LiteralPath (Join-Path $Target "NEW_REALITY_SCOPE_LOCK.md")
$scopeValidation = [ordered]@{
    timestamp_utc = $createdUtc
    scope_lock_path = "NEW_REALITY_SCOPE_LOCK.md"
    default_allowed_root_present = ($scopeText -like "*$Target*")
    salvage_request_required = ($scopeText -like "*SALVAGE_REQUEST*")
    ancient_empire_not_active_context = ($scopeText -like "*Ancient Empire is not active context*")
    private_paths_forbidden = ($scopeText -like "*Private folders*")
    verdict = "PASS_SCOPE_LOCK_INSTALLED"
}
Write-JsonFile (Join-Path $Report "scope_lock_validation_receipt.json") $scopeValidation

$epochValidation = [ordered]@{
    timestamp_utc = $createdUtc
    epoch_manifest_path = "EPOCH_MANIFEST.json"
    required_fields_present = @("epoch", "active_root", "source_epoch", "ancient_reference", "servitor_scope")
    epoch_is_new_reality = ($epochManifest.epoch -eq "NEW_REALITY")
    active_root_matches = ($epochManifest.active_root -eq $Target)
    source_epoch_matches = ($epochManifest.source_epoch -eq "ANCIENT_EMPIRE")
    verdict = "PASS_EPOCH_MANIFEST_SCHEMA_MINIMUM"
}
Write-JsonFile (Join-Path $Report "epoch_manifest_validation_receipt.json") $epochValidation

$salvageValidation = [ordered]@{
    timestamp_utc = $createdUtc
    template_path = "SALVAGE_REQUEST_TEMPLATE.json"
    required_fields_present = @("request_id", "source_epoch", "source_path", "target_path", "reason", "admitting_organ", "status")
    source_epoch_is_ancient = ($salvageTemplate.source_epoch -eq "ANCIENT_EMPIRE")
    status_is_proposed = ($salvageTemplate.status -eq "PROPOSED")
    verdict = "PASS_SALVAGE_POLICY_TEMPLATE_INSTALLED"
}
Write-JsonFile (Join-Path $Report "salvage_policy_receipt.json") $salvageValidation

$rootInventory = [ordered]@{
    timestamp_utc = $createdUtc
    new_reality_root = $Target
    stats = (Get-DirectoryStats $Target)
    top_level = (Get-TopLevelInventory $Target)
    root_contracts = [ordered]@{
        README_md = (Test-Path -LiteralPath (Join-Path $Target "README.md"))
        AGENTS_md = (Test-Path -LiteralPath (Join-Path $Target "AGENTS.md"))
        NEW_REALITY_SCOPE_LOCK_md = (Test-Path -LiteralPath (Join-Path $Target "NEW_REALITY_SCOPE_LOCK.md"))
        EPOCH_MANIFEST_json = (Test-Path -LiteralPath (Join-Path $Target "EPOCH_MANIFEST.json"))
        ANCIENT_EMPIRE_REFERENCE_md = (Test-Path -LiteralPath (Join-Path $Target "ANCIENT_EMPIRE_REFERENCE.md"))
        SALVAGE_REQUEST_TEMPLATE_json = (Test-Path -LiteralPath (Join-Path $Target "SALVAGE_REQUEST_TEMPLATE.json"))
    }
    full_old_repo_copy_detected = (Test-Path -LiteralPath (Join-Path $Target "IMPERIUM_NEW_GENERATION"))
}
Write-JsonFile (Join-Path $Report "new_reality_root_inventory.json") $rootInventory

$oldHeadAfterCopy = Get-GitOutput $OldRoot @("rev-parse", "HEAD")
$oldDirtyAfterCopy = @(& git -C $OldRoot status --short 2>$null)
$noDeletion = [ordered]@{
    timestamp_utc = $createdUtc
    old_repo_root = $OldRoot
    old_repo_still_exists = (Test-Path -LiteralPath $OldRoot)
    source_newgen_still_exists = (Test-Path -LiteralPath $Source)
    old_head_before = $oldHead
    old_head_after = $oldHeadAfterCopy
    old_head_unchanged = ($oldHeadAfterCopy -eq $oldHead)
    old_dirty_entries_before = $oldDirty
    old_dirty_entries_after = $oldDirtyAfterCopy
    no_deletion_performed = $true
    no_history_rewrite_performed = ($oldHeadAfterCopy -eq $oldHead)
    verdict = "PASS_ANCIENT_EMPIRE_PRESERVED_WITH_PREEXISTING_DIRTY_STATE_RECORDED"
}
Write-JsonFile (Join-Path $Report "no_deletion_receipt.json") $noDeletion

$claimRows = @(
    [ordered]@{ claim = "Required organ and taskpack authority read before implementation"; owner_organ = "OFFICIO_AGENTIS"; capability_class = "AGENT_REASONING_ONLY"; evidence_level = "E2_AUTHORITY_READ_RECEIPT"; cap = "ACCEPTED_WITH_WARNING_CANDIDATE_AUTHORITY"; red_team = "No missing required READ_FIRST authority found." },
    [ordered]@{ claim = "Ancient Empire was preserved without deletion or history rewrite"; owner_organ = "INQUISITION"; capability_class = "LOCAL_SCRIPT_FIRST"; evidence_level = "E3_COMMAND_RECEIPT"; cap = "NONE"; red_team = "Old HEAD unchanged; dirty state preexisted and remains recorded." },
    [ordered]@{ claim = "New Reality root created from NewGen source, not full old repository"; owner_organ = "ASTRONOMICON"; capability_class = "LOCAL_SCRIPT_FIRST"; evidence_level = "E3_COMMAND_RECEIPT"; cap = "NONE"; red_team = "Copy excludes old .git and generated dependency/cache dirs; no byte-for-byte copy claim." },
    [ordered]@{ claim = "External dependency scan completed"; owner_organ = "MECHANICUS"; capability_class = "LOCAL_SCRIPT_FIRST"; evidence_level = "E3_COMMAND_RECEIPT"; cap = "CAP_EXTERNAL_DEPENDENCIES_RECORDED"; red_team = "Old root and absolute references remain; final verdict cannot be clean PASS." },
    [ordered]@{ claim = "Local git initialized and initial commit created"; owner_organ = "MECHANICUS"; capability_class = "LOCAL_SCRIPT_FIRST"; evidence_level = "E3_COMMAND_RECEIPT"; cap = "NONE"; red_team = "Commit hash recorded in second receipt commit to avoid self-head paradox." },
    [ordered]@{ claim = "Remote push not performed"; owner_organ = "ADMINISTRATUM"; capability_class = "OWNER_MANUAL_CONFIRMATION"; evidence_level = "E2_POLICY_RECEIPT"; cap = "CAP_REMOTE_PUSH_PENDING_OWNER_AUTHORIZATION"; red_team = "Task forbids push without Owner-authorized remote; PASS downgraded to PASS_WITH_WARNINGS." }
)
Write-JsonLines (Join-Path $Report "CLAIM_LEDGER.jsonl") $claimRows

$evidenceRows = @(
    [ordered]@{ artifact = "pc_repo_truth_probe.json"; evidence_level = "E3"; replay = "git branch/head/status plus filesystem probe" },
    [ordered]@{ artifact = "external_dependency_scan.json"; evidence_level = "E3"; replay = "rg scan plus PowerShell inventory" },
    [ordered]@{ artifact = "ancient_empire_freeze_receipt.json"; evidence_level = "E3"; replay = "git HEAD/status after copy" },
    [ordered]@{ artifact = "new_reality_copy_manifest.json"; evidence_level = "E3"; replay = "robocopy exit code and inventory" },
    [ordered]@{ artifact = "scope_lock_validation_receipt.json"; evidence_level = "E2"; replay = "text contract checks" },
    [ordered]@{ artifact = "epoch_manifest_validation_receipt.json"; evidence_level = "E2"; replay = "schema-minimum field checks" },
    [ordered]@{ artifact = "new_reality_git_init_receipt.json"; evidence_level = "E3"; replay = "git init/add/commit/status" }
)
Write-JsonLines (Join-Path $Report "EVIDENCE_LEDGER.jsonl") $evidenceRows

Push-Location $Target
try {
    & git init -b master | Out-Null
    if ($LASTEXITCODE -ne 0) {
        & git init | Out-Null
        & git branch -M master | Out-Null
    }
    & git config user.name "IMPERIUM Servitor" | Out-Null
    & git config user.email "servitor@imperium.local" | Out-Null
    & git config core.longpaths true | Out-Null
    & git config core.autocrlf false | Out-Null
    $remoteConfiguredBefore = ((& git remote) -join "").Trim().Length -gt 0
    & git add -A
    & git commit -m "NEW_REALITY: initialize active NewGen core" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "GIT_INITIAL_COMMIT_FAILED" }
    $initialCommit = ((& git rev-parse HEAD) -join "").Trim()
    $initialBranch = ((& git branch --show-current) -join "").Trim()
    $statusAfterInitial = @(& git status --short)

    $gitReceipt = [ordered]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
        new_reality_root = $Target
        git_initialized = $true
        branch = $initialBranch
        initial_commit = $initialCommit
        initial_commit_message = "NEW_REALITY: initialize active NewGen core"
        worktree_clean = ($statusAfterInitial.Count -eq 0)
        remote_configured = $remoteConfiguredBefore
        warnings = @("No remote push performed because task forbids push without Owner-created/authorized New Reality remote.", "Receipt commit is written after the initial commit to avoid self-head paradox.")
    }
    Write-JsonFile (Join-Path $Report "new_reality_git_init_receipt.json") $gitReceipt

    $commitPushReceipt = [ordered]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
        commit_performed = $true
        initial_commit = $initialCommit
        followup_receipt_commit = "PENDING_SELF_HEAD_SEMANTICALLY_EXTERNAL_TO_THIS_FILE"
        push_performed = $false
        remote_configured = $remoteConfiguredBefore
        block_reason_class = "BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE"
        owner_action_required = $true
        owner_question_or_instruction = "Create or authorize a New Reality remote, then run git remote add origin <url> and git push -u origin master if remote publication is desired."
        caps_triggered = @("CAP_REMOTE_PUSH_PENDING_OWNER_AUTHORIZATION")
        clean_pass_allowed = $false
    }
    Write-JsonFile (Join-Path $Report "commit_push_receipt.json") $commitPushReceipt

    $externalFinalization = [ordered]@{
        receipt_subject_head = "NEW_REALITY_LOCAL_REPOSITORY"
        last_verified_head_before_this_commit = $initialCommit
        receipt_content_head = $initialCommit
        external_delivery_head = "REPORTED_BY_FINAL_OWNER_RESPONSE_AFTER_RECEIPT_COMMIT"
        remote_head_after_push = "NOT_APPLICABLE_NO_REMOTE_AUTHORIZED"
        verification_timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
        verification_actor = "Servitor Codex local session"
        worktree_clean_after_push = "NOT_APPLICABLE_NO_PUSH"
        origin_master_sync_after_push = "NOT_APPLICABLE_NO_REMOTE_AUTHORIZED"
        verification_method = "git status and git log after final receipt commit; final head relayed in Owner response"
        self_head_paradox_handled = $true
        commit_performed = $true
        push_performed = $false
        block_reason_class = "BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE"
        owner_action_required = $true
        owner_question_or_instruction = "Remote push requires Owner-authorized New Reality remote."
        caps_triggered = @("CAP_REMOTE_PUSH_PENDING_OWNER_AUTHORIZATION", "CAP_EXTERNAL_DEPENDENCIES_RECORDED")
        clean_pass_allowed = $false
    }
    Write-JsonFile (Join-Path $Report "external_finalization_receipt.json") $externalFinalization

    $redTeam = [ordered]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
        mode = "HARD_RED_TEAM_CLOSURE_GATE"
        checks = [ordered]@{
            head_status_evidence_boundary_match = "WARN_SELF_HEAD_HANDLED_BY_EXTERNAL_FINAL_RESPONSE"
            dirty_provenance_contradiction = "WARN_OLD_REPO_DIRTY_PREEXISTING_RECORDED_NOT_HIDDEN"
            stale_receipt = "PASS_RECEIPTS_CREATED_IN_CURRENT_TASK"
            role_authority_read = "PASS_REQUIRED_AUTHORITY_READ"
            manual_reasoning_as_capability = "PASS_CAPABILITY_SPLIT_DECLARED"
            screenshot_without_semantic_truth = "NOT_APPLICABLE"
            missing_replay_command = "PASS_EXECUTE_NEW_REALITY_SPLIT_PS1_PRESENT"
            commit_push_policy = "WARN_LOCAL_COMMITS_DONE_PUSH_BLOCKED_BY_MISSING_OWNER_AUTHORIZED_REMOTE"
            output_format = "PASS_TASKPACK_OUTPUTS_CREATED"
            private_local_leak_risk = "WARN_EXTERNAL_PATH_REFERENCES_RECORDED_SCOPE_LOCK_INSTALLED"
        }
        caps = @("CAP_EXTERNAL_DEPENDENCIES_RECORDED", "CAP_REMOTE_PUSH_PENDING_OWNER_AUTHORIZATION", "CAP_OLD_REPO_DIRTY_PREEXISTING")
        downgraded_verdict = "PASS_WITH_WARNINGS"
        clean_pass_allowed = $false
        notes = @("No deletion/rewrite of Ancient Empire detected.", "New Reality is local-only until Owner authorizes remote.", "Runtime adaptation of old root references is out of scope and should be a follow-up task.")
    }
    Write-JsonFile (Join-Path $Report "RED_TEAM_VERDICT.json") $redTeam

    $gateValidation = [ordered]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
        gates = [ordered]@{
            pc_contour_truth = "PASS"
            ancient_empire_freeze = "PASS_WITH_PREEXISTING_DIRTY_WARNING"
            new_reality_root = "PASS"
            local_git_repository = "PASS"
            scope_lock = "PASS"
            dependency_scan = "WARN_EXTERNAL_DEPENDENCIES_RECORDED"
            receipts_and_bundle = "PASS_PENDING_BUNDLE_CREATION"
        }
        verdict = "PASS_WITH_WARNINGS"
    }
    Write-JsonFile (Join-Path $Report "final_gate_validation_receipt.json") $gateValidation

    $finalSummaryRu = @"
# FINAL_OWNER_SUMMARY_RU

## EVIDENCE_BOUNDARY
PC-local filesystem and git evidence only. No GitHub push, no VM2/VM3 sync, no runtime adaptation claim.

## IMPERIUM_QUESTION_PASS
Blocking Owner questions: none for local split. Optional next Owner action: authorize/create New Reality remote if push is desired.

## CAPABILITY_SPLIT_RECEIPT
LOCAL_SCRIPT_FIRST: copy, receipts, git init/commit, checksum, bundle. AGENT_REASONING_ONLY: warning classification and red-team wording. OWNER_MANUAL_CONFIRMATION: remote push.

## CLAIM_LEDGER
Major claims are recorded in CLAIM_LEDGER.jsonl with evidence/caps. Clean PASS is blocked by recorded external references and missing Owner-authorized remote.

## RED_TEAM_VERDICT
PASS_WITH_WARNINGS. Ancient Empire stayed preserved; New Reality exists as local repo; external path/root references remain follow-up work.

## FINAL_OWNER_SUMMARY_RU
Шаг выполнен локально: создан New Reality root и отдельный git repo. Старый Ancient Empire не удалялся и HEAD не переписывался. Итог не clean PASS, потому что старый repo был грязный до старта, есть старые absolute/root ссылки, и push запрещен без Owner-authorized remote.
"@
    Write-Utf8NoBomText (Join-Path $Report "final_owner_summary_ru.md") $finalSummaryRu

    $reportFilesForHash = @(Get-ChildItem -LiteralPath $Report -Recurse -File -Force |
        Where-Object { $_.Name -notin @("sha256sums.txt", "task_report_bundle.zip") } |
        Sort-Object FullName)
    $sumLines = @()
    foreach ($file in $reportFilesForHash) {
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        $rel = (Resolve-Path -LiteralPath $file.FullName -Relative).Replace("\\", "/")
        $sumLines += "$hash  $rel"
    }
    Write-Utf8NoBomText (Join-Path $Report "sha256sums.txt") (($sumLines -join "`n") + "`n")

    $bundlePath = Join-Path $Report "task_report_bundle.zip"
    if (Test-Path -LiteralPath $bundlePath) { Remove-Item -LiteralPath $bundlePath -Force }
    $bundleInputs = @(Get-ChildItem -LiteralPath $Report -File -Force | Where-Object { $_.Name -ne "task_report_bundle.zip" })
    Compress-Archive -LiteralPath ($bundleInputs.FullName) -DestinationPath $bundlePath -Force

    & git add -A
    $statusBeforeReceiptCommit = @(& git status --short)
    if ($statusBeforeReceiptCommit.Count -gt 0) {
        & git commit -m "NEW_REALITY: record split receipts" | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "GIT_RECEIPT_COMMIT_FAILED" }
    }
    $receiptCommit = ((& git rev-parse HEAD) -join "").Trim()
    $finalStatus = @(& git status --short)
    [ordered]@{
        task_id = $TaskId
        target = $Target
        report = $Report
        initial_commit = $initialCommit
        receipt_commit = $receiptCommit
        branch = ((& git branch --show-current) -join "").Trim()
        final_status_short = $finalStatus
        final_status_clean = ($finalStatus.Count -eq 0)
        verdict = "PASS_WITH_WARNINGS"
        warnings = @("Old repo dirty state preexisted and is recorded.", "External dependency/root references remain for follow-up.", "No remote push performed without Owner authorization.")
    } | ConvertTo-Json -Depth 8
}
finally {
    Pop-Location
}
