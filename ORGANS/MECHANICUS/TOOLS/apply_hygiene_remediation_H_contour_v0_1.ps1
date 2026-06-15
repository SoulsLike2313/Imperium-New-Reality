#Requires -Version 7.6
<#
.SYNOPSIS
    IMPERIUM New Reality Hygiene & Honesty Remediation - H-contour (Handy/manual) apply tool (PowerShell 7.6.2).

.DESCRIPTION
    Applies the patch pack FIX-1..FIX-14 into the H-contour (Handy = handmade/manual work & checks) sandbox / warp-zone MIRROR repo (suffix marker '_H'). It is integrated FIRST into the *_H mirror; the canonical repo is touched only after manual review.
    Safe by default: runs as a dry-run unless -Apply is given, and supports -WhatIf / -Confirm.
    Machine receipts are written ENGLISH UTF-8 NO-BOM LF. A Russian owner summary is generated separately.
    Capability tag: LOCAL_SCRIPT_FIRST.

.NOTES
    Phases mirror Ghost_Evolve V2:
      ROLE_ENTRY_ACK -> EVIDENCE_BOUNDARY -> PRE_SCAN -> REMEDIATION -> CAPABILITY_SPLIT
      -> POST_SCAN -> GIT_TRUTH -> RED_TEAM_RESCAN -> VERDICT_AND_RESIDUE

.EXAMPLE
    pwsh ./apply_hygiene_remediation_H_contour_v0_1.ps1 -RepoRoot 'E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H'        # dry-run (no -Apply)
.EXAMPLE
    pwsh ./apply_hygiene_remediation_H_contour_v0_1.ps1 -RepoRoot 'E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H' -Apply
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Low')]
param(
    [Parameter(Mandatory)] [string] $RepoRoot,
    [switch] $Apply,
    [string] $RemoteRef = 'origin/master',
    [switch] $SkipGit,
    [switch] $IncludeLegacyQuarantine,
    [switch] $Force,
    [string] $TaskId = 'TASK-20260614-PC-NEW-REALITY-HYGIENE-AND-HONESTY-REMEDIATION-V0_1',
    [string] $Contour = 'H',
    [string] $MirrorMarker = '_H',           # Handy/manual H-contour mirror suffix; change if your mirror uses another marker
    [int] $MaxSamples = 25
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'
$script:IsApply = [bool]$Apply

# ---------- small helpers ----------
function Write-Step { param([string]$Msg) Write-Host ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $Msg) -ForegroundColor Cyan }
function Write-Ok   { param([string]$Msg) Write-Host ("  OK  {0}" -f $Msg) -ForegroundColor Green }
function Write-Warn2{ param([string]$Msg) Write-Host ("  !!  {0}" -f $Msg) -ForegroundColor Yellow }
function Write-Block{ param([string]$Msg) Write-Host ("  XX  {0}" -f $Msg) -ForegroundColor Red }

function Write-Utf8NoBom {
    param([string]$Path, [string]$Text)
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force -WhatIf:$false -Confirm:$false | Out-Null }
    $enc = [System.Text.UTF8Encoding]::new($false)        # NO BOM
    $norm = $Text -replace "`r`n", "`n"                     # force LF
    [System.IO.File]::WriteAllText($Path, $norm, $enc)
}

function Write-Receipt {
    param([string]$Name, [hashtable]$Body)
    $path = Join-Path $script:ReportDir $Name
    $json = $Body | ConvertTo-Json -Depth 12
    Write-Utf8NoBom -Path $path -Text $json
    Write-Ok ("receipt -> {0}" -f $Name)
}

$TextExt   = @('.md','.json','.jsonl','.py','.txt','.toml','.js','.ts','.tsx','.css','.tcss','.html','.svg','.yml','.yaml')
$KeepCrlf  = @('.ps1','.cmd','.bat')
$ArtDirs   = @('target','node_modules','__pycache__','.pytest_cache')
$ArtExt    = @('.rlib','.rmeta','.pdb','.dll','.exe','.lib','.pyc','.pyo')
$FixMarker = @('FIXTURE','FIXTURES','fixture','fixtures')
$SecretAllow = @('QUESTIONABLE_OR_QUARANTINE','validate_organ_dialogue_demo')
$SecretRx  = @(
    'AKIA[0-9A-Z]{16}',
    'ghp_[A-Za-z0-9]{20,}',
    '-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
    'xox[baprs]-[A-Za-z0-9-]{10,}'
)
$Bom = [byte[]](0xEF,0xBB,0xBF)

function Test-Allowlisted { param([string]$Rel,[string[]]$Markers) foreach ($m in $Markers) { if ($Rel -like "*$m*") { return $true } } return $false }

function Get-PrunedFiles {
    # BFS that skips .git and artifact dirs entirely.
    param([string]$Root)
    $stack = [System.Collections.Generic.Stack[string]]::new()
    $stack.Push($Root)
    while ($stack.Count -gt 0) {
        $dir = $stack.Pop()
        foreach ($child in [System.IO.Directory]::EnumerateDirectories($dir)) {
            $leaf = Split-Path $child -Leaf
            if ($leaf -eq '.git' -or $ArtDirs -contains $leaf) { continue }
            try { if (([System.IO.File]::GetAttributes($child) -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { continue } } catch { continue }
            $stack.Push($child)
        }
        foreach ($f in [System.IO.Directory]::EnumerateFiles($dir)) {
            if ((Split-Path $f -Leaf) -eq '.git') { continue }
            try { if (([System.IO.File]::GetAttributes($f) -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { continue } } catch { continue }
            $f
        }
    }
}

function Get-HygieneReport {
    param([string]$Root)
    $r = [ordered]@{
        build_artifact_files = 0; build_artifact_bytes = 0L
        committed_zip = 0; bom_files = 0; crlf_files = 0
        truly_malformed_json = 0; bom_only_json = 0; empty_files = 0; secret_like = 0
    }
    $samples = [ordered]@{ build_artifact_files=@(); committed_zip=@(); bom_files=@(); crlf_files=@(); truly_malformed_json=@(); empty_files=@(); secret_like=@() }
    # artifact directories (counted whole)
    foreach ($ad in $ArtDirs) {
        Get-ChildItem -LiteralPath $Root -Directory -Recurse -Force -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq $ad -and $_.FullName -notmatch '[\\/]\.git[\\/]' } |
            ForEach-Object {
                $files = Get-ChildItem -LiteralPath $_.FullName -File -Recurse -Force -ErrorAction SilentlyContinue
                $r.build_artifact_files += @($files).Count
                $r.build_artifact_bytes += (($files | Measure-Object Length -Sum).Sum ?? 0)
                if ($samples.build_artifact_files.Count -lt $MaxSamples) { $samples.build_artifact_files += ($_.FullName.Substring($Root.Length).TrimStart('\','/') -replace '\\','/') }
            }
    }
    foreach ($f in Get-PrunedFiles -Root $Root) {
        $ext = [System.IO.Path]::GetExtension($f).ToLower()
        $name = [System.IO.Path]::GetFileName($f)
        $rel = $f.Substring($Root.Length).TrimStart('\','/') -replace '\\','/'
        $len = 0L
        try { $len = ([System.IO.FileInfo]::new($f)).Length } catch { continue }
        if ($ArtExt -contains $ext) { $r.build_artifact_files++; $r.build_artifact_bytes += $len; continue }
        if ($ext -eq '.zip') { if (-not (Test-Allowlisted $rel $FixMarker)) { $r.committed_zip++; if ($samples.committed_zip.Count -lt $MaxSamples){$samples.committed_zip+=$rel} }; continue }
        if ($len -eq 0 -and $name -ne '.gitkeep') { $r.empty_files++; if ($samples.empty_files.Count -lt $MaxSamples){$samples.empty_files+=$rel} }
        $head = [byte[]]::new(0)
        try { $fs=[System.IO.File]::OpenRead($f); $buf=[byte[]]::new([Math]::Min(65536,$len)); [void]$fs.Read($buf,0,$buf.Length); $fs.Close(); $head=$buf } catch {}
        $startsBom = ($head.Length -ge 3 -and $head[0] -eq 0xEF -and $head[1] -eq 0xBB -and $head[2] -eq 0xBF)
        if (($ext -eq '.json' -or $ext -eq '.md') -and $startsBom) { $r.bom_files++; if ($samples.bom_files.Count -lt $MaxSamples){$samples.bom_files+=$rel} }
        if ($TextExt -contains $ext -and ($head -contains 0x0D)) { $r.crlf_files++; if ($samples.crlf_files.Count -lt $MaxSamples){$samples.crlf_files+=$rel} }
        if ($ext -eq '.json') {
            try { Get-Content -LiteralPath $f -Raw -Encoding utf8 | ConvertFrom-Json -Depth 64 | Out-Null; if ($startsBom){$r.bom_only_json++} }
            catch { if (-not (Test-Allowlisted $rel $FixMarker)) { $r.truly_malformed_json++; if ($samples.truly_malformed_json.Count -lt $MaxSamples){$samples.truly_malformed_json+=$rel} } }
        }
        if ($TextExt -contains $ext -and -not (Test-Allowlisted $rel $SecretAllow)) {
            $txt = [System.Text.Encoding]::UTF8.GetString($head)
            foreach ($rx in $SecretRx) { if ($txt -match $rx) { $r.secret_like++; if ($samples.secret_like.Count -lt $MaxSamples){$samples.secret_like+=$rel}; break } }
        }
    }
    $block = ($r.build_artifact_files -gt 0 -or $r.committed_zip -gt 0 -or $r.truly_malformed_json -gt 0 -or $r.secret_like -gt 0)
    $warn  = ($r.bom_files -gt 0 -or $r.crlf_files -gt 0 -or $r.empty_files -gt 0)
    $verdict = if ($block) { 'BLOCK' } elseif ($warn) { 'PASS_WITH_WARNINGS' } else { 'PASS' }
    $r['build_artifact_megabytes'] = [math]::Round($r.build_artifact_bytes/1MB,1)
    return [ordered]@{
        schema_version='imperium.hygiene_gate_report.v0_1'; tool='apply_hygiene_remediation_H_contour_v0_1.ps1'
        capability_tag='LOCAL_SCRIPT_FIRST'; repo_root=$Root; contour=$Contour; counts=$r; samples=$samples; verdict=$verdict
    }
}

# ============================ PHASE 0: ROLE_ENTRY_ACK ============================
Write-Step 'PHASE ROLE_ENTRY_ACK'
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$leaf = Split-Path $RepoRoot -Leaf
$isMirror = ($leaf -like "*$MirrorMarker*") -or ($leaf -match '(?i)(_H$|MIRROR|HANDY|WARP)')
if (-not $isMirror -and -not $Force) {
    Write-Block ("Refusing: '{0}' does not look like an H-contour mirror (suffix marker '{1}'). Use -Force to override." -f $leaf,$MirrorMarker)
    throw 'N_MIRROR_GUARD_TRIGGERED'
}
$script:ReportDir = Join-Path $RepoRoot ("REPORTS/{0}" -f $TaskId)
$script:BackupRoot = Join-Path $script:ReportDir 'BACKUP'
New-Item -ItemType Directory -Path $script:ReportDir -Force -WhatIf:$false -Confirm:$false | Out-Null
$runId = (Get-Date -Format 'yyyyMMdd_HHmmss')
Write-Receipt 'ROLE_ENTRY_RECEIPT.json' @{
    schema_version='imperium.officio.role_entry_receipt.v0_1'; task_id=$TaskId; contour=$Contour
    role='SERVITOR'; entered_through='OFFICIO_AGENTIS'; run_id=$runId
    mode = ($script:IsApply ? 'APPLY' : 'DRY_RUN'); mirror_guard = ($isMirror ? 'PASS' : 'FORCED')
    owner_language='RUSSIAN'; machine_language='ENGLISH_UTF8_NO_BOM'
}
Write-Ok ("role entered. mode={0} repo={1}" -f ($script:IsApply ? 'APPLY' : 'DRY_RUN'), $RepoRoot)

# ============================ PHASE 1: EVIDENCE_BOUNDARY ============================
Write-Step 'PHASE EVIDENCE_BOUNDARY'
$gitPresent = Test-Path -LiteralPath (Join-Path $RepoRoot '.git')
$head = $null
if ($gitPresent -and -not $SkipGit) { try { $head = (git -C $RepoRoot rev-parse HEAD).Trim() } catch { $head = $null } }
Write-Receipt 'EVIDENCE_BOUNDARY_RECEIPT.json' @{
    schema_version='imperium.evidence_boundary.v0_1'; task_id=$TaskId; git_present=$gitPresent
    repo_head = ($head ?? 'AUTHORITY_GAP_NO_GIT'); inputs=@('patch pack tools','templates'); dirty_state_declared=$true
}
if (-not $gitPresent) { Write-Warn2 'No .git in mirror: git-truth will be AUTHORITY_GAP, not PASS.' }

# ============================ PHASE 2: PRE_SCAN ============================
Write-Step 'PHASE PRE_SCAN (hygiene gate before)'
$before = Get-HygieneReport -Root $RepoRoot
Write-Receipt 'HYGIENE_GATE_REPORT_BEFORE.json' ([hashtable]$before)
Write-Host ("  before verdict = {0} | artifacts={1} ({2} MB) zip={3} bom={4} crlf={5} empty={6}" -f `
    $before.verdict,$before.counts.build_artifact_files,$before.counts.build_artifact_megabytes,`
    $before.counts.committed_zip,$before.counts.bom_files,$before.counts.crlf_files,$before.counts.empty_files) -ForegroundColor Gray

# ============================ PHASE 3: REMEDIATION ============================
Write-Step 'PHASE REMEDIATION'
$PackRoot = Split-Path $PSScriptRoot -Parent
$delta = [System.Collections.Generic.List[object]]::new()
function Backup-File { param([string]$Full)
    $rel = $Full.Substring($RepoRoot.Length).TrimStart('\','/')
    $dst = Join-Path $script:BackupRoot $rel
    $d = Split-Path $dst -Parent
    if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d -Force -WhatIf:$false -Confirm:$false | Out-Null }
    Copy-Item -LiteralPath $Full -Destination $dst -Force
}

# FIX-1 .gitignore + FIX-4 .gitattributes/.editorconfig
foreach ($pair in @(
    @{ tpl='templates/gitignore_additions.txt'; dst='.gitignore'; append=$true },
    @{ tpl='templates/.gitattributes.template'; dst='.gitattributes'; append=$false },
    @{ tpl='templates/.editorconfig.template';  dst='.editorconfig';  append=$false }
)) {
    $tplPath = Join-Path $PackRoot $pair.tpl
    $dstPath = Join-Path $RepoRoot $pair.dst
    if (-not (Test-Path -LiteralPath $tplPath)) { Write-Warn2 ("template missing: {0}" -f $pair.tpl); continue }
    $content = Get-Content -LiteralPath $tplPath -Raw
    if ($PSCmdlet.ShouldProcess($dstPath, ($pair.append ? 'append .gitignore rules' : 'write config'))) {
        if ($script:IsApply) {
            if ((Test-Path -LiteralPath $dstPath) ) { Backup-File $dstPath }
            if ($pair.append -and (Test-Path -LiteralPath $dstPath)) {
                $existing = Get-Content -LiteralPath $dstPath -Raw
                if ($existing -notmatch '(?m)^\s*\*\*/target/\s*$') { Write-Utf8NoBom -Path $dstPath -Text ($existing.TrimEnd() + "`n`n" + $content) }
            } else { Write-Utf8NoBom -Path $dstPath -Text $content }
        }
        $delta.Add(@{ action=($pair.append ? 'append' : 'write'); path=$pair.dst })
        Write-Ok $pair.dst
    }
}

# FIX-2 remove build artifacts (+ git rm --cached)
Write-Step 'FIX-2 build artifacts'
$artHits = [System.Collections.Generic.List[object]]::new()
foreach ($ad in $ArtDirs) {
    Get-ChildItem -LiteralPath $RepoRoot -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq $ad -and $_.FullName -notmatch '[\\/]\.git[\\/]' } |
        ForEach-Object {
            $sz = ((Get-ChildItem -LiteralPath $_.FullName -File -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum ?? 0)
            $rel = $_.FullName.Substring($RepoRoot.Length).TrimStart('\','/') -replace '\\','/'
            $artHits.Add(@{ path=$rel; megabytes=[math]::Round($sz/1MB,1) })
            if ($PSCmdlet.ShouldProcess($_.FullName, 'remove artifact dir')) {
                if ($script:IsApply) {
                    if ($gitPresent -and -not $SkipGit) { git -C $RepoRoot rm -r --cached --quiet -- "$rel" 2>$null | Out-Null }
                    Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
                }
                $delta.Add(@{ action='remove_dir'; path=$rel })
            }
        }
}
Write-Ok ("artifact dirs: {0} (reclaim {1} MB)" -f $artHits.Count, (($artHits.megabytes | Measure-Object -Sum).Sum ?? 0))

# FIX-3/FIX-4 encoding: strip BOM + CRLF->LF (skip fixtures, keep ps1/cmd CRLF)
Write-Step 'FIX-3/4 encoding (BOM + CRLF)'
$bomFixed = 0; $crlfFixed = 0
foreach ($f in Get-PrunedFiles -Root $RepoRoot) {
    $ext = [System.IO.Path]::GetExtension($f).ToLower()
    if ($TextExt -notcontains $ext -and $KeepCrlf -notcontains $ext) { continue }
    $rel = $f.Substring($RepoRoot.Length).TrimStart('\','/') -replace '\\','/'
    if (Test-Allowlisted $rel $FixMarker) { continue }
    try { $bytes = [System.IO.File]::ReadAllBytes($f) } catch { continue }
    $orig = $bytes
    if (($ext -eq '.json' -or $ext -eq '.md') -and $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $bytes = [byte[]]($bytes[3..($bytes.Length-1)]); $bomFixed++
    }
    if ($KeepCrlf -notcontains $ext -and ($bytes -contains 0x0D)) {
        $txt = [System.Text.Encoding]::UTF8.GetString($bytes) -replace "`r`n","`n" -replace "`r","`n"
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($txt); $crlfFixed++
    }
    if ($bytes.Length -ne $orig.Length -or (Compare-Object $bytes $orig -SyncWindow 0)) {
        if ($PSCmdlet.ShouldProcess($rel,'normalize encoding')) {
            if ($script:IsApply) { Backup-File $f; [System.IO.File]::WriteAllBytes($f, $bytes) }
        }
    }
}
Write-Ok ("encoding: bom_stripped={0} crlf_fixed={1}" -f $bomFixed,$crlfFixed)

# FIX-8 empty files (keep .gitkeep)
Write-Step 'FIX-8 empty files'
$emptyRemoved = 0
foreach ($f in Get-PrunedFiles -Root $RepoRoot) {
    $elen = -1L; try { $elen = ([System.IO.FileInfo]::new($f)).Length } catch { continue }
    if ($elen -eq 0 -and (Split-Path $f -Leaf) -ne '.gitkeep') {
        $rel = $f.Substring($RepoRoot.Length).TrimStart('\','/') -replace '\\','/'
        if (Test-Allowlisted $rel $FixMarker) { continue }
        if ($PSCmdlet.ShouldProcess($rel,'remove empty file')) {
            if ($script:IsApply) { if($gitPresent -and -not $SkipGit){ git -C $RepoRoot rm --cached --quiet -- "$rel" 2>$null | Out-Null }; Remove-Item -LiteralPath $f -Force }
            $emptyRemoved++; $delta.Add(@{ action='remove_empty'; path=$rel })
        }
    }
}
Write-Ok ("empty files removed: {0}" -f $emptyRemoved)

# FIX-6 committed zip outside FIXTURES (report only; relocation needs owner decision)
Write-Step 'FIX-6 committed zip inventory'
$zipHits = @()
foreach ($f in Get-PrunedFiles -Root $RepoRoot) {
    if ([System.IO.Path]::GetExtension($f).ToLower() -eq '.zip') {
        $rel = $f.Substring($RepoRoot.Length).TrimStart('\','/') -replace '\\','/'
        if (-not (Test-Allowlisted $rel $FixMarker)) { $zipHits += $rel }
    }
}
Write-Receipt 'COMMITTED_ZIP_INVENTORY.json' @{ schema_version='imperium.zip_inventory.v0_1'; task_id=$TaskId; count=$zipHits.Count; zips=($zipHits | Select-Object -First $MaxSamples); note='Relocation/removal needs owner decision; not auto-deleted.' }
Write-Warn2 ("committed zip outside FIXTURES: {0} (left for owner decision)" -f $zipHits.Count)

# FIX-7 LEGACY_IMPORTED_ROOT_MIRROR detection / optional quarantine
Write-Step 'FIX-7 legacy mirror'
$legacy = Get-ChildItem -LiteralPath $RepoRoot -Directory -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq 'LEGACY_IMPORTED_ROOT_MIRROR' } | ForEach-Object { $_.FullName.Substring($RepoRoot.Length).TrimStart('\','/') -replace '\\','/' }
if ($legacy -and $IncludeLegacyQuarantine) {
    $q = Join-Path $RepoRoot 'SUPPORT/QUARANTINE'
    foreach ($lp in $legacy) {
        if ($PSCmdlet.ShouldProcess($lp,'move to SUPPORT/QUARANTINE')) {
            if ($script:IsApply) { New-Item -ItemType Directory -Path $q -Force | Out-Null; Move-Item -LiteralPath (Join-Path $RepoRoot $lp) -Destination (Join-Path $q (Split-Path $lp -Parent | Split-Path -Leaf)) -Force -ErrorAction SilentlyContinue }
            $delta.Add(@{ action='quarantine_legacy'; path=$lp })
        }
    }
}
Write-Ok ("legacy mirror dirs: {0} (quarantine={1})" -f (@($legacy).Count), $IncludeLegacyQuarantine)

# FIX-9 STRATEGIUM true cleanliness metric v0.2
Write-Step 'FIX-9 metric v0.2'
$metricTplPath = Join-Path $PackRoot 'organ_teaching/STRATEGIUM_TRUE_CLEANLINESS_METRIC_V0_2.json'
if (Test-Path -LiteralPath $metricTplPath) {
    $metricDst = Join-Path $RepoRoot 'ORGANS/STRATEGIUM/METRICS/true_physical_cleanliness_metric_v0_2.json'
    if ($PSCmdlet.ShouldProcess($metricDst,'install metric v0.2')) {
        if ($script:IsApply) { Write-Utf8NoBom -Path $metricDst -Text (Get-Content -LiteralPath $metricTplPath -Raw) }
        $delta.Add(@{ action='install_metric'; path='ORGANS/STRATEGIUM/METRICS/true_physical_cleanliness_metric_v0_2.json' })
    }
}

# Install organ teaching artifacts (ULTIMATE_ORGAN_TEACHING)
Write-Step 'Install organ teaching artifacts'
$teachMap = @{
    'organ_teaching/DOCTRINARIUM_LAW_CLEAN_AND_HONEST_SYSTEM_V0_1.md' = 'ORGANS/DOCTRINARIUM/LAWS/CLEAN_AND_HONEST_SYSTEM_LAW_V0_1.md'
    'organ_teaching/MECHANICUS_HYGIENE_GATE_TOOL_CARD_V0_1.md'        = 'ORGANS/MECHANICUS/TOOL_CARDS/HYGIENE_GATE_TOOL_CARD_V0_1.md'
    'organ_teaching/INQUISITION_HYGIENE_FAKE_GREEN_MATRIX_V0_1.json'  = 'ORGANS/INQUISITION/MATRICES/HYGIENE_FAKE_GREEN_MATRIX_V0_1.json'
    'organ_teaching/ADMINISTRATUM_RECEIPT_ENCODING_AND_GIT_TRUTH_V0_1.md' = 'ORGANS/ADMINISTRATUM/CONTRACTS/RECEIPT_ENCODING_REMEDIATION_NOTE_V0_1.md'
    'organ_teaching/CUSTODES_ARTIFACT_BOUNDARY_AUDIT_V0_1.md'         = 'ORGANS/CUSTODES/ORGAN_MATRIX_AUDIT/ARTIFACT_BOUNDARY_AUDIT_V0_1.md'
    'organ_teaching/SCHOLA_LESSON_AND_ENHANCED_GHOST_EVOLVE_V0_1.md'  = 'ORGANS/SCHOLA_IMPERIALIS/LESSONS/LESSON_HYGIENE_HONESTY_V0_1.md'
}
foreach ($src in $teachMap.Keys) {
    $s = Join-Path $PackRoot $src
    if (-not (Test-Path -LiteralPath $s)) { continue }
    $d = Join-Path $RepoRoot $teachMap[$src]
    if ($PSCmdlet.ShouldProcess($d,'install teaching artifact')) {
        if ($script:IsApply) { Write-Utf8NoBom -Path $d -Text (Get-Content -LiteralPath $s -Raw) }
        $delta.Add(@{ action='install_teaching'; path=$teachMap[$src] })
    }
}

# Also copy the runnable tools into MECHANICUS so the organs own them
foreach ($t in @('imperium_hygiene_gate_v0_1.py','fix_encoding_bom_crlf_v0_1.py','remove_build_artifacts_v0_1.py','verify_git_truth_v0_1.py','apply_hygiene_remediation_H_contour_v0_1.ps1')) {
    $s = Join-Path $PSScriptRoot $t
    if (-not (Test-Path -LiteralPath $s)) { continue }
    $d = Join-Path $RepoRoot ("ORGANS/MECHANICUS/TOOLS/{0}" -f $t)
    if ($PSCmdlet.ShouldProcess($d,'install tool')) {
        if ($script:IsApply) { Write-Utf8NoBom -Path $d -Text (Get-Content -LiteralPath $s -Raw) }
        $delta.Add(@{ action='install_tool'; path=("ORGANS/MECHANICUS/TOOLS/{0}" -f $t) })
    }
}

# ============================ PHASE 4: CAPABILITY_SPLIT ============================
Write-Receipt 'CAPABILITY_SPLIT_RECEIPT.json' @{
    schema_version='imperium.capability_split.v0_1'; task_id=$TaskId
    LOCAL_SCRIPT_FIRST=@('hygiene scan','bom/crlf fix','artifact removal','metric v0.2','teaching install')
    LOCAL_MANUAL_COMMAND=@('git commit','git push')
    OWNER_MANUAL_CONFIRMATION=@('delete/relocate committed zip','quarantine LEGACY mirror without -IncludeLegacyQuarantine')
    FUTURE_CAPABILITY_GAP=@('rewrite git history to drop 885 MB from past commits (git filter-repo / BFG)')
}

# ============================ PHASE 5: POST_SCAN ============================
Write-Step 'PHASE POST_SCAN (hygiene gate after)'
$after = Get-HygieneReport -Root $RepoRoot
Write-Receipt 'HYGIENE_GATE_REPORT_AFTER.json' ([hashtable]$after)

# FIX-2 removal receipt
Write-Receipt 'BUILD_ARTIFACT_REMOVAL_RECEIPT.json' @{ schema_version='imperium.artifact_removal.v0_1'; task_id=$TaskId; mode=($script:IsApply ? 'APPLY' : 'DRY_RUN'); dirs=$artHits; reclaim_megabytes=(($artHits.megabytes | Measure-Object -Sum).Sum ?? 0) }
Write-Receipt 'ENCODING_NORMALIZATION_RECEIPT.json' @{ schema_version='imperium.encoding_norm.v0_1'; task_id=$TaskId; mode=($script:IsApply ? 'APPLY' : 'DRY_RUN'); bom_stripped=$bomFixed; crlf_fixed=$crlfFixed; fixtures_preserved=$true }

# ============================ PHASE 6: GIT_TRUTH ============================
Write-Step 'PHASE GIT_TRUTH'
$gitVerdict = 'AUTHORITY_GAP'; $clean=$false; $remoteOk=$false; $remoteHead=$null
if ($gitPresent -and -not $SkipGit) {
    $status = (git -C $RepoRoot status --porcelain=v1)
    $clean = [string]::IsNullOrWhiteSpace(($status | Out-String))
    try { $remoteHead = (git -C $RepoRoot rev-parse $RemoteRef 2>$null).Trim() } catch { $remoteHead=$null }
    $remoteOk = ($remoteHead -and $remoteHead -eq $head)
    $gitVerdict = ($clean -and $remoteOk) ? 'PASS' : 'BLOCK'
}
Write-Receipt 'GIT_TRUTH_RECEIPT.json' @{
    schema_version='imperium.pre_push_gate_receipt.v0_1'; tool='apply_hygiene_remediation_H_contour_v0_1.ps1'
    capability_tag='LOCAL_SCRIPT_FIRST'; repo_root=$RepoRoot; git_present=$gitPresent
    working_tree_clean=$clean; local_head=($head ?? $null); remote_ref=$RemoteRef; remote_head=$remoteHead
    head_equals_remote=$remoteOk; verdict=$gitVerdict
}

# ============================ PHASE 7: RED_TEAM_RESCAN ============================
$ringVerdict = if ($after.verdict -eq 'BLOCK' -or $gitVerdict -eq 'BLOCK') { 'BLOCK' }
               elseif ($after.verdict -eq 'PASS' -and $gitVerdict -eq 'PASS') { 'PASS' }
               else { 'PASS_WITH_WARNINGS' }
Write-Receipt 'RED_TEAM_VERDICT.json' @{
    task_id=$TaskId
    builder_claims=@(
        @{ claim='build artifacts removed'; evidence='HYGIENE_GATE_REPORT_AFTER.json'; capability_tag='LOCAL_SCRIPT_FIRST' },
        @{ claim='encoding normalized'; evidence='ENCODING_NORMALIZATION_RECEIPT.json'; capability_tag='LOCAL_SCRIPT_FIRST' }
    )
    attacks=@(
        @{ attack='dry-run mislabeled as applied'; defense=("mode field = " + ($script:IsApply ? 'APPLY' : 'DRY_RUN')) },
        @{ attack='ran against canonical repo not mirror'; defense=('H-contour mirror guard, marker=' + $MirrorMarker) },
        @{ attack='clean claimed without git'; defense='git-truth verdict = ' + $gitVerdict }
    )
    downgrade_rules_applied=@('no_fake_green','downgrade_on_missing_git_truth')
    final_verdict=$ringVerdict
}

# ============================ PHASE 8: VERDICT_AND_RESIDUE ============================
Write-Receipt 'POST_WORK_FILE_DELTA_INDEX.json' @{ schema_version='imperium.file_delta_index.v0_1'; task_id=$TaskId; mode=($script:IsApply ? 'APPLY' : 'DRY_RUN'); changes=$delta }
Write-Receipt 'POST_WORK_ORGAN_RING_RECEIPT.json' @{
    schema_version='imperium.post_work_organ_ring_receipt.v0_1'; task_id=$TaskId; run_id=$runId
    repo_head=($head ?? 'AUTHORITY_GAP'); ring_verdict=$ringVerdict
    organs=@{ ASTRONOMICON='route';OFFICIO_AGENTIS='role+language';DOCTRINARIUM='law';MECHANICUS='tools';ADMINISTRATUM='receipts+git';INQUISITION='fake-green';STRATEGIUM='metric v0.2';CUSTODES='boundary audit';SCHOLA_IMPERIALIS='lesson' }
}
Write-Receipt 'NEXT_TASK_ROUTE.json' @{ schema_version='imperium.next_task_route.v0_1'; task_id=$TaskId; next=@('Owner reviews dry-run delta','Approve -Apply on H-mirror','Commit+push on mirror','Promote to canonical repo after Custodes audit','History purge decision (FUTURE_CAPABILITY_GAP)') }

# Russian owner summary (owner-facing, routed through OFFICIO)
$ru = @"
# Итог Н-контур (язык владельца)

Режим: $([string]($script:IsApply ? 'ПРИМЕНЕНО (APPLY)' : 'СУХОЙ ПРОГОН (DRY_RUN)'))
Зеркало: $RepoRoot
Защита зеркала: $([string]($isMirror ? 'PASS' : 'FORCED'))

## До
вердикт=$($before.verdict); артефакты=$($before.counts.build_artifact_files) ($($before.counts.build_artifact_megabytes) МБ); zip=$($before.counts.committed_zip); BOM=$($before.counts.bom_files); CRLF=$($before.counts.crlf_files); пустые=$($before.counts.empty_files)

## После
вердикт=$($after.verdict); артефакты=$($after.counts.build_artifact_files) ($($after.counts.build_artifact_megabytes) МБ); zip=$($after.counts.committed_zip); BOM=$($after.counts.bom_files); CRLF=$($after.counts.crlf_files); пустые=$($after.counts.empty_files)

## Git-правда
вердикт=$gitVerdict (нет .git => AUTHORITY_GAP, а не фейк-PASS)

## Общий вердикт кольца: $ringVerdict

Намеренные сломанные фикстуры и ложные "секреты" не тронуты. zip и LEGACY-зеркало оставлены на твоё решение.
PASS_WITH_WARNINGS не выдаётся за чистый PASS.
"@
Write-Utf8NoBom -Path (Join-Path $script:ReportDir 'FINAL_OWNER_SUMMARY_RU.md') -Text $ru

Write-Step ('DONE. verdict={0} mode={1}' -f $ringVerdict, ($script:IsApply ? 'APPLY' : 'DRY_RUN'))
Write-Host ('Reports: ' + $script:ReportDir) -ForegroundColor Green
if (-not $script:IsApply) { Write-Warn2 'This was a DRY_RUN. Re-run with -Apply to write changes into the H-contour (*_H) mirror.' }
exit ([int]($ringVerdict -eq 'BLOCK' ? 2 : ($ringVerdict -eq 'PASS_WITH_WARNINGS' ? 1 : 0)))
