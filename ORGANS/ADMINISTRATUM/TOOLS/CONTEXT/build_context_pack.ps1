[CmdletBinding()]
param(
  [string]$RealityRoot = 'E:\IMPERIUM_REALITY',
  [string]$HarnessRoot = 'E:\IMPERIUM_HARNESS',
  [string]$OutDir      = 'E:\IMPERIUM_HARNESS\CONTINUITY_OUT\CONTEXT',
  [int]$LogN           = 200,
  [switch]$Apply
)
$ErrorActionPreference = 'Continue'
try { $PSNativeCommandUseErrorActionPreference = $false } catch {}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$enc = New-Object System.Text.UTF8Encoding $false
function Write-LF {
  param($p, $t)
  $d = Split-Path -Parent $p
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
  if ($null -eq $t) { $t = '' }
  [System.IO.File]::WriteAllText($p, (($t) -replace "`r`n", "`n"), $enc)
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$pack  = Join-Path $OutDir "IMPERIUM_CONTEXT_PACK_$stamp"
$mode  = if ($Apply) { 'APPLY' } else { 'DRY-RUN' }

Write-Host "================================================================"
Write-Host "  ADMINISTRATUM CONTEXT PACK ASSEMBLER v0_1  [$mode]"
Write-Host "  RealityRoot : $RealityRoot"
Write-Host "  HarnessRoot : $HarnessRoot"
Write-Host "  OutPack     : $pack"
Write-Host "================================================================"

# ---------- preflight ----------
$fail = $false
if (-not (Test-Path $RealityRoot)) { Write-Host "FAIL: нет RealityRoot $RealityRoot"; $fail = $true }
$wStart = Join-Path $HarnessRoot 'TOOLS\WARP\warp-start.ps1'
$wLand  = Join-Path $HarnessRoot 'TOOLS\WARP\warp-land.ps1'
if (-not (Test-Path $wStart)) { Write-Host "FAIL: нет $wStart"; $fail = $true }
if (-not (Test-Path $wLand))  { Write-Host "FAIL: нет $wLand"; $fail = $true }
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) { Write-Host 'FAIL: git не найден в PATH'; $fail = $true }
$py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) { Write-Host 'FAIL: python не найден в PATH'; $fail = $true }
if (-not (Test-Path (Join-Path $scriptDir 'context_pack_lib.py')))    { Write-Host 'FAIL: нет context_pack_lib.py рядом'; $fail = $true }
if (-not (Test-Path (Join-Path $scriptDir 'verify_context_pack.py'))) { Write-Host 'FAIL: нет verify_context_pack.py рядом'; $fail = $true }
if ($fail) { Write-Host 'VERDICT: CONTEXT_PACK_FAIL'; exit 1 }

$head = (& git -C $RealityRoot rev-parse HEAD).Trim()

Write-Host '--- ПЛАН ---'
Write-Host "  git_head        : $head"
Write-Host "  + TOOLCHAIN/    <- $HarnessRoot\TOOLS (+ ORGANS\ASTRONOMICON\TOOLS)"
Write-Host '  + HISTORY/      <- git head/log/numstat/status/changed/branches/remotes (локальный терминал)'
Write-Host '  + STATE/        <- CONTINUITY_MANIFEST.json + warp_active.json'
Write-Host '  + DOCTRINE/     <- FORM (если есть)'
Write-Host '  + MANIFEST.json <- python context_pack_lib build (sha256 каждого файла)'
Write-Host '  + verify        <- python verify_context_pack (SELF_SUFFICIENT_OK)'

if (-not $Apply) { Write-Host 'VERDICT: CONTEXT_PACK_DRYRUN_OK (запусти с -Apply)'; exit 0 }

# ---------- TOOLCHAIN ----------
$tc = Join-Path $pack 'TOOLCHAIN\HARNESS\TOOLS'
New-Item -ItemType Directory -Force -Path $tc | Out-Null
Copy-Item -Recurse -Force (Join-Path $HarnessRoot 'TOOLS\*') $tc
$astro = Join-Path $RealityRoot 'ORGANS\ASTRONOMICON\TOOLS'
if (Test-Path $astro) {
  $dst = Join-Path $pack 'TOOLCHAIN\REALITY\ORGANS\ASTRONOMICON\TOOLS'
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  Copy-Item -Recurse -Force (Join-Path $astro '*') $dst
}

# ---------- HISTORY (локальный терминальный git) ----------
Write-LF (Join-Path $pack 'HISTORY\git_head.txt') $head
Write-LF (Join-Path $pack 'HISTORY\git_log.txt')      ((& git -C $RealityRoot log -n $LogN --date=iso --pretty='format:%H|%ad|%an|%s') -join "`n")
Write-LF (Join-Path $pack 'HISTORY\git_numstat.txt')  ((& git -C $RealityRoot log -n $LogN --numstat --pretty='format:--- %H %s') -join "`n")
Write-LF (Join-Path $pack 'HISTORY\git_status.txt')   ((& git -C $RealityRoot status --porcelain) -join "`n")
Write-LF (Join-Path $pack 'HISTORY\changed_files.txt') ((& git -C $RealityRoot log -n $LogN --shortstat --pretty='format:%H %s') -join "`n")
Write-LF (Join-Path $pack 'HISTORY\branches.txt')     ((& git -C $RealityRoot branch -a) -join "`n")
Write-LF (Join-Path $pack 'HISTORY\remotes.txt')      ((& git -C $RealityRoot remote -v) -join "`n")

# ---------- STATE ----------
$cont = Join-Path $HarnessRoot 'CONTINUITY_OUT'
if (Test-Path $cont) {
  Get-ChildItem -Recurse -File -Path $cont -Include 'CONTINUITY_MANIFEST.json', 'warp_active.json' -ErrorAction SilentlyContinue |
    ForEach-Object { Copy-Item -Force $_.FullName (Join-Path $pack ('STATE\' + $_.Name)) }
}
if (-not (Test-Path (Join-Path $pack 'STATE\continuity_manifest.json'))) {
  $srcCm = Join-Path $pack 'STATE\CONTINUITY_MANIFEST.json'
  if (Test-Path $srcCm) { Copy-Item -Force $srcCm (Join-Path $pack 'STATE\continuity_manifest.json') }
  else { Write-LF (Join-Path $pack 'STATE\continuity_manifest.json') '{}' }
}

# ---------- DOCTRINE ----------
$form = Join-Path $RealityRoot 'FORM'
if (Test-Path $form) {
  $dst = Join-Path $pack 'DOCTRINE\FORM'
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  Copy-Item -Recurse -Force (Join-Path $form '*') $dst
} else {
  New-Item -ItemType Directory -Force -Path (Join-Path $pack 'DOCTRINE') | Out-Null
  Write-LF (Join-Path $pack 'DOCTRINE\NOTE.txt') 'FORM не найден в RealityРoot на момент сборки.'
}

# ---------- CONTEXT_ENTRY.md ----------
$entry = "# IMPERIUM — CONTEXT ENTRY (самодостаточный пак)`n`n" +
  "git_head: $head`n`n" +
  "Этот пак = 100% вход в контекст. Гит — лёгкая локальная страховка/чтение, источник истины = пак.`n`n" +
  "Порядок чтения:`n" +
  "1. STATE/      — состояние, роль, HEAD, активный WARP.`n" +
  "2. TOOLCHAIN/  — полный исходник исполняемого слоя (warp-start/warp-land, инсталляторы).`n" +
  "3. HISTORY/    — локальный git: HEAD, лог, numstat, статус, число изменённых файлов.`n" +
  "4. DOCTRINE/   — FORM и законы.`n" +
  "5. MANIFEST.json — sha256 каждого файла (целостность).`n"
Write-LF (Join-Path $pack 'CONTEXT_ENTRY.md') $entry

# ---------- MANIFEST + VERIFY (единый источник истины) ----------
& $py.Source (Join-Path $scriptDir 'context_pack_lib.py') build $pack --git-head $head --note 'administratum context pack'
& $py.Source (Join-Path $scriptDir 'verify_context_pack.py') $pack --expect-head $head
if ($LASTEXITCODE -ne 0) { Write-Host 'VERDICT: CONTEXT_PACK_FAIL'; exit 1 }

Write-Host "  pack ready: $pack"
Write-Host 'VERDICT: CONTEXT_PACK_OK'
