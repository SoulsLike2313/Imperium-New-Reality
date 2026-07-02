param(
  [switch]$SelfTest
)

$ErrorActionPreference = "Stop"

function Write-JsonAndExit {
  param([hashtable]$Data, [int]$Code)
  $Data | ConvertTo-Json -Depth 40
  exit $Code
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$AppRoot = $PSScriptRoot

$ManifestPath = Join-Path $RepoRoot "SUPPORT\APP\IMPERIUM_LAUNCHER_APP_MANIFEST_V0_2.json"
$ThemePath = Join-Path $RepoRoot "SUPPORT\APP\IMPERIUM_SYSTEM_LEVELING_THEME_V0_2.json"
$ActionsPath = Join-Path $RepoRoot "SUPPORT\TUI\IMPERIUM_TUI_ACTIONS_V0_1.json"
$ConsoleTui = Join-Path $RepoRoot "SUPPORT\TUI\imperium_tui.py"

$AppLogDir = Join-Path $RepoRoot "SUPPORT\APP\LOGS"
$AppReceiptDir = Join-Path $RepoRoot "SUPPORT\APP\RECEIPTS"
$PackRequestDir = Join-Path $RepoRoot "SUPPORT\APP\REGISTRY\PACK_REQUESTS"
$TuiLogDir = Join-Path $RepoRoot "SUPPORT\TUI\LOGS"
$TuiReceiptDir = Join-Path $RepoRoot "SUPPORT\TUI\RECEIPTS"

function Read-Json($Path) {
  if (-not (Test-Path $Path)) { return $null }
  try { return Get-Content $Path -Raw | ConvertFrom-Json } catch { return $null }
}

$Manifest = Read-Json $ManifestPath
$Theme = Read-Json $ThemePath
$ActionsManifest = Read-Json $ActionsPath
$Actions = @()
if ($ActionsManifest -and $ActionsManifest.actions) { $Actions = @($ActionsManifest.actions) }

$OrganRooms = @(
  [pscustomobject]@{ id="ASTRONOMICON"; title="ASTRONOMICON"; ru="Астрономикон"; status="CROWN-CONFIRMED 1/10"; unlocked=$true; actions=@("status","astronomicon-advice","astronomicon-redblue","astronomicon-hardening","score-refresh-guidance") },
  [pscustomobject]@{ id="CUSTODES"; title="CUSTODES"; ru="Кустодес"; status="Прокурор органа"; unlocked=$true; actions=@("custodes-audit","custodes-readout") },
  [pscustomobject]@{ id="THRONE"; title="THRONE"; ru="Трон"; status="Crown order / anti-self-deception"; unlocked=$true; actions=@("throne-crown-order","throne-readout") },
  [pscustomobject]@{ id="PACK_FORGE"; title="PACK FORGE"; ru="Кузница паков"; status="Patch/Task registration requests"; unlocked=$true; actions=@("register-patch-pack","register-task-pack") },
  [pscustomobject]@{ id="ADMINISTRATUM"; title="ADMINISTRATUM"; ru="Администратум"; status="locked until organ room"; unlocked=$false; actions=@() },
  [pscustomobject]@{ id="MECHANICUS"; title="MECHANICUS"; ru="Механикус"; status="locked until organ room"; unlocked=$false; actions=@() },
  [pscustomobject]@{ id="INQUISITION"; title="INQUISITION"; ru="Инквизиция"; status="locked until organ room"; unlocked=$false; actions=@() }
)

if ($SelfTest) {
  $errors = New-Object System.Collections.Generic.List[string]

  foreach ($p in @($ManifestPath, $ThemePath, $ActionsPath, $ConsoleTui)) {
    if (-not (Test-Path $p)) { $errors.Add("missing dependency: $p") }
  }

  if (-not $Manifest) { $errors.Add("manifest parse failed") }
  if (-not $Theme) { $errors.Add("theme parse failed") }
  if ($Actions.Count -lt 8) { $errors.Add("action count below threshold") }

  foreach ($a in $Actions) {
    if ([string]::IsNullOrWhiteSpace($a.ru_label)) { $errors.Add("missing action ru_label: $($a.id)") }
    if ([string]::IsNullOrWhiteSpace($a.ru_description)) { $errors.Add("missing action ru_description: $($a.id)") }
    if ($a.aquarium_log_required -ne $true) { $errors.Add("aquarium not required: $($a.id)") }
  }

  try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
  } catch {
    $errors.Add("cannot load Windows Forms: $($_.Exception.Message)")
  }

  $scriptText = Get-Content $PSCommandPath -Raw
  foreach ($needle in @(
    "ORGAN_HUB",
    "IMPERIUM LEVELING SYSTEM",
    "Proof XP",
    "Стрик",
    "Войти в орган",
    "ASTRONOMICON",
    "CUSTODES",
    "THRONE",
    "PACK FORGE",
    "Регистрация Patch Pack",
    "Регистрация Task Pack",
    "Register-PackRequest",
    "Load-OrganRoom",
    "CROWN_AWARE_OVERLAY",
    "AQUARIUM",
    "Calculate-Leveling",
    "Refresh-Leveling"
  )) {
    if ($scriptText -notlike "*$needle*") { $errors.Add("missing app marker: $needle") }
  }

  $unlockedCount = @($OrganRooms | Where-Object { $_.unlocked }).Count
  if ($unlockedCount -lt 4) { $errors.Add("not enough unlocked rooms") }

  $verdict = if ($errors.Count -eq 0) { "PASS_IMPERIUM_LAUNCHER_APP_ORGAN_HUB_LEVELING_SELFTEST" } else { "FAIL_IMPERIUM_LAUNCHER_APP_ORGAN_HUB_LEVELING_SELFTEST" }
  $code = if ($errors.Count -eq 0) { 0 } else { 1 }

  Write-JsonAndExit @{
    task_id = "IMPERIUM-LAUNCHER-APP-ORGAN-HUB-LEVELING-UI-0001"
    validator_id = "imperium_launcher_app_organ_hub_leveling_selftest.v0_1"
    verdict = $verdict
    action_count = $Actions.Count
    organ_room_count = $OrganRooms.Count
    unlocked_organ_room_count = $unlockedCount
    app_id = if ($Manifest) { $Manifest.app_id } else { $null }
    theme_id = if ($Theme) { $Theme.theme_id } else { $null }
    errors = @($errors)
    warnings = @()
  } $code
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

New-Item -ItemType Directory -Force -Path $AppLogDir | Out-Null
New-Item -ItemType Directory -Force -Path $AppReceiptDir | Out-Null
New-Item -ItemType Directory -Force -Path $PackRequestDir | Out-Null
New-Item -ItemType Directory -Force -Path $TuiLogDir | Out-Null
New-Item -ItemType Directory -Force -Path $TuiReceiptDir | Out-Null

function ColorFromHex([string]$hex, [string]$fallback) {
  if ([string]::IsNullOrWhiteSpace($hex)) { $hex = $fallback }
  return [System.Drawing.ColorTranslator]::FromHtml($hex)
}

$Colors = $Theme.colors
$C_Void = ColorFromHex $Colors.void "#07070B"
$C_Back = ColorFromHex $Colors.background "#0B0B12"
$C_Panel = ColorFromHex $Colors.panel "#151320"
$C_PanelAlt = ColorFromHex $Colors.panel_alt "#1D182A"
$C_PanelDeep = ColorFromHex $Colors.panel_deep "#0D0B14"
$C_Line = ColorFromHex $Colors.line "#3A3159"
$C_Text = ColorFromHex $Colors.text "#E8E0CF"
$C_Muted = ColorFromHex $Colors.muted "#A69A7D"
$C_Gold = ColorFromHex $Colors.gold "#D8B75B"
$C_GoldDark = ColorFromHex $Colors.gold_dark "#6F5520"
$C_Purple = ColorFromHex $Colors.purple "#8B4DFF"
$C_PurpleDeep = ColorFromHex $Colors.purple_deep "#402070"
$C_Cyan = ColorFromHex $Colors.cyan "#66D9EF"
$C_Red = ColorFromHex $Colors.red "#B34A4A"
$C_Green = ColorFromHex $Colors.green "#61B36B"
$C_LogBack = ColorFromHex $Colors.log_background "#050507"
$C_LogText = ColorFromHex $Colors.log_text "#D7D7D7"

$script:CurrentAction = $null
$script:CurrentOrgan = $null
$script:CurrentTranscript = New-Object System.Text.StringBuilder

function Add-Log {
  param([string]$Text, [string]$Level = "INFO")
  $timestamp = (Get-Date).ToString("HH:mm:ss")
  $line = "[$timestamp][$Level] $Text"
  $script:LogBox.SelectionStart = $script:LogBox.TextLength
  if ($Level -eq "ERROR") { $script:LogBox.SelectionColor = $C_Red }
  elseif ($Level -eq "PASS") { $script:LogBox.SelectionColor = $C_Green }
  elseif ($Level -eq "AUTH") { $script:LogBox.SelectionColor = $C_Gold }
  elseif ($Level -eq "XP") { $script:LogBox.SelectionColor = $C_Purple }
  else { $script:LogBox.SelectionColor = $C_LogText }
  $script:LogBox.AppendText($line + [Environment]::NewLine)
  $script:LogBox.SelectionStart = $script:LogBox.TextLength
  $script:LogBox.ScrollToCaret()
  [void]$script:CurrentTranscript.AppendLine($line)
  [System.Windows.Forms.Application]::DoEvents()
}

function Save-AppTranscript {
  param([string]$ActionId)
  if ([string]::IsNullOrWhiteSpace($ActionId)) { $ActionId = "app" }
  $stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
  $safe = ($ActionId -replace '[^A-Za-z0-9_.-]+', '_')
  $path = Join-Path $AppLogDir "${stamp}_app_${safe}.log"
  $script:CurrentTranscript.ToString() | Set-Content -Path $path -Encoding UTF8
  Add-Log "APP_LOG_SAVED: $($path.Replace($RepoRoot + '\',''))" "AUTH"
}

function Get-Json($RelPath) {
  $p = Join-Path $RepoRoot $RelPath
  if (-not (Test-Path $p)) { return $null }
  try { return Get-Content $p -Raw | ConvertFrom-Json } catch { return $null }
}

function Format-Value($v) {
  if ($null -eq $v) { return "—" }
  return [string]$v
}

function Get-CleanStreak {
  $files = @()
  foreach ($dir in @($TuiReceiptDir, $AppReceiptDir, (Join-Path $RepoRoot "ORGANS\ASTRONOMICON\RECEIPTS"), (Join-Path $RepoRoot "ORGANS\THRONE\RECEIPTS"), (Join-Path $RepoRoot "ORGANS\CUSTODES\RECEIPTS"))) {
    if (Test-Path $dir) {
      $files += Get-ChildItem $dir -File -Filter "*.json" -ErrorAction SilentlyContinue
    }
  }
  $files = $files | Sort-Object LastWriteTime -Descending | Select-Object -First 60
  $streak = 0
  foreach ($f in $files) {
    try { $j = Get-Content $f.FullName -Raw | ConvertFrom-Json } catch { break }
    $ok = $false
    if ($null -ne $j.exit_code) { $ok = ([int]$j.exit_code -eq 0) }
    elseif ($j.verdict) { $ok = ([string]$j.verdict).StartsWith("PASS") }
    elseif ($j.errors -is [array]) { $ok = ($j.errors.Count -eq 0) }
    if ($ok) { $streak++ } else { break }
  }
  return $streak
}

function Calculate-Leveling {
  $readout = Get-Json "ORGANS\THRONE\REPORTS\POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json"
  $xp = 0
  $reasons = New-Object System.Collections.Generic.List[string]

  if ($readout -and $readout.astronomicon_chain_ok -eq $true) { $xp += 100; $reasons.Add("+100 Astronomicon chain ok") }
  if ($readout -and $readout.stage_integrates_local_crown -eq $true) { $xp += 100; $reasons.Add("+100 CROWN_AWARE_OVERLAY") }

  if ($readout -and $readout.crown_aware_scores) {
    foreach ($k in @(
      "red_team_score",
      "blue_team_score",
      "custodes_organ_validators_score",
      "throne_organ_validators_score",
      "trust_proven_score",
      "rule_validated_score",
      "tui_launcher_presence_score",
      "throne_confirmed_score"
    )) {
      $v = $readout.crown_aware_scores.$k
      if ($null -ne $v) { $xp += [int][double]$v; $reasons.Add("+$v $k") }
    }
    if ($readout.crown_aware_scores.organ_assembled_score -eq 0) { $xp += 25; $reasons.Add("+25 honesty: assembled remains 0") }
  }

  $throne = Get-Json "ORGANS\THRONE\REPORTS\THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json"
  if ($throne -and $throne.throne_self_validation_score -eq 0) { $xp += 25; $reasons.Add("+25 honesty: Throne self-validation remains 0") }

  $streak = Get-CleanStreak
  $streakBonus = [Math]::Min($streak * 5, 100)
  $xp += $streakBonus
  $reasons.Add("+$streakBonus clean execution streak ($streak)")

  $level = [Math]::Floor($xp / 100) + 1
  $levelProgress = $xp % 100

  return [pscustomobject]@{
    xp = $xp
    level = $level
    level_progress = $levelProgress
    streak = $streak
    reasons = @($reasons)
  }
}

function Refresh-Leveling {
  $lvl = Calculate-Leveling
  $script:LevelLabel.Text = "LEVEL $($lvl.level)"
  $script:XPLabel.Text = "Proof XP: $($lvl.xp)   |   Стрик: $($lvl.streak) чистых receipts"
  $script:XPBar.Value = [Math]::Max(0, [Math]::Min(100, [int]$lvl.level_progress))
  $script:XPDetailsBox.Clear()
  $script:XPDetailsBox.AppendText("IMPERIUM LEVELING SYSTEM" + [Environment]::NewLine)
  $script:XPDetailsBox.AppendText("Опыт начисляется только за доказанную функциональность и чистые исполнения." + [Environment]::NewLine + [Environment]::NewLine)
  foreach ($r in $lvl.reasons) {
    $script:XPDetailsBox.AppendText("$r" + [Environment]::NewLine)
  }
}

function Refresh-Status {
  $readout = Get-Json "ORGANS\THRONE\REPORTS\POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json"
  $throne = Get-Json "ORGANS\THRONE\REPORTS\THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json"
  $custodes = Get-Json "ORGANS\CUSTODES\REPORTS\CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json"

  $script:StatusBox.Clear()
  $script:StatusBox.SelectionColor = $C_Gold
  $script:StatusBox.AppendText("IMPERIUM STATUS / ORGAN HUB" + [Environment]::NewLine)
  $script:StatusBox.SelectionColor = $C_Text
  $script:StatusBox.AppendText("Repo: $RepoRoot" + [Environment]::NewLine)

  if ($readout) {
    $script:StatusBox.AppendText("" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Astronomicon chain ok: $(Format-Value $readout.astronomicon_chain_ok)" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Stage integrates local crown: $(Format-Value $readout.stage_integrates_local_crown)" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Stage integration mode: $(Format-Value $readout.stage_integration_mode)" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Integration note: $(Format-Value $readout.integration_note)" + [Environment]::NewLine)

    if ($readout.crown_aware_scores) {
      $c = $readout.crown_aware_scores
      $script:StatusBox.AppendText("" + [Environment]::NewLine)
      $script:StatusBox.AppendText("CROWN_AWARE_OVERLAY" + [Environment]::NewLine)
      foreach ($k in @("red_team_score","blue_team_score","custodes_organ_validators_score","throne_organ_validators_score","trust_proven_score","rule_validated_score","tui_launcher_presence_score","throne_confirmed_score","organ_truth_maturity_score_crown_aware_estimate","organ_assembled_score")) {
        $script:StatusBox.AppendText("${k}: $(Format-Value $c.$k)" + [Environment]::NewLine)
      }
    }
  }

  if ($custodes) {
    $script:StatusBox.AppendText("" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Custodes verdict: $(Format-Value $custodes.verdict)" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Custodes score: $(Format-Value $custodes.custodes_validation_score)" + [Environment]::NewLine)
  }

  if ($throne) {
    $script:StatusBox.AppendText("" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Throne verdict: $(Format-Value $throne.verdict)" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Throne self-validation: $(Format-Value $throne.throne_self_validation_score)" + [Environment]::NewLine)
    $script:StatusBox.AppendText("Astronomicon assembled: $(Format-Value $throne.astronomicon_assembled_score)" + [Environment]::NewLine)
  }

  Refresh-Leveling
}

function Load-OrganRoom {
  param([object]$Room)

  if (-not $Room.unlocked) {
    Add-Log "Organ locked: $($Room.title). Build its organ room later." "ERROR"
    return
  }

  $script:CurrentOrgan = $Room
  $script:OrganTitle.Text = "$($Room.title) / $($Room.ru)"
  $script:OrganSubtitle.Text = $Room.status
  $script:OrganActionList.Items.Clear()

  foreach ($actionId in $Room.actions) {
    if ($actionId -eq "register-patch-pack") {
      $label = "Регистрация Patch Pack"
      $desc = "Создать app-level заявку на регистрацию Patch Pack."
      $mode = "request"
    } elseif ($actionId -eq "register-task-pack") {
      $label = "Регистрация Task Pack"
      $desc = "Создать app-level заявку на регистрацию Task Pack."
      $mode = "request"
    } else {
      $a = $Actions | Where-Object { $_.id -eq $actionId } | Select-Object -First 1
      if (-not $a) { continue }
      $label = $a.ru_label
      $desc = $a.ru_description
      $mode = if ($a.mutates_repo) { "writes" } else { "read" }
    }

    $item = New-Object System.Windows.Forms.ListViewItem($actionId)
    [void]$item.SubItems.Add($label)
    [void]$item.SubItems.Add($mode)
    [void]$item.SubItems.Add($desc)
    $item.Tag = $actionId
    [void]$script:OrganActionList.Items.Add($item)
  }

  $script:Tabs.SelectedTab = $script:TabOrgan
  Add-Log "Entered organ room: $($Room.title)" "AUTH"
}

function Update-OrganDetails {
  if ($script:OrganActionList.SelectedItems.Count -eq 0) { return }
  $id = $script:OrganActionList.SelectedItems[0].Tag

  if ($id -eq "register-patch-pack") {
    $script:DetailsBox.Text = "Регистрация Patch Pack`r`nСоздаёт app-level request draft. Не claim canonical registration."
    return
  }
  if ($id -eq "register-task-pack") {
    $script:DetailsBox.Text = "Регистрация Task Pack`r`nСоздаёт app-level request draft. Не claim canonical registration."
    return
  }

  $a = $Actions | Where-Object { $_.id -eq $id } | Select-Object -First 1
  if (-not $a) { return }
  $script:DetailsBox.Text = @"
Функция:
$($a.ru_label)

ID:
$($a.id)

Описание:
$($a.ru_description)

Тип:
$($a.kind)

Пишет repo:
$($a.mutates_repo)

Аквариум:
$($a.aquarium_log_required)
"@
}

function Register-PackRequest {
  param([string]$Kind)

  $packId = $script:PackIdBox.Text.Trim()
  $title = $script:PackTitleBox.Text.Trim()
  $organ = [string]$script:PackOrganBox.SelectedItem

  if ([string]::IsNullOrWhiteSpace($packId)) {
    [System.Windows.Forms.MessageBox]::Show("Укажи Pack ID.", "Pack Forge") | Out-Null
    return
  }
  if ([string]::IsNullOrWhiteSpace($title)) { $title = $packId }
  if ([string]::IsNullOrWhiteSpace($organ)) { $organ = "ASTRONOMICON" }

  $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
  $safe = ($packId -replace '[^A-Za-z0-9_.-]+', '_')
  $requestPath = Join-Path $PackRequestDir "${stamp}_${Kind}_${safe}.json"
  $receiptPath = Join-Path $AppReceiptDir "${stamp}_${Kind}_${safe}_pack_registration_request_receipt.json"

  $request = [ordered]@{
    request_id = "app.pack_registration_request.$stamp.$safe"
    kind = $Kind
    pack_id = $packId
    title = $title
    target_organ = $organ
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    status = "APP_REQUEST_DRAFT_NOT_CANONICAL_REGISTRATION"
    boundary = @(
      "This is a Launcher App registration request draft.",
      "It does not claim canonical Astronomicon/Administratum registration.",
      "A later organ-level registrar must accept or reject it."
    )
  }
  $receipt = [ordered]@{
    receipt_id = "receipt.app.pack_registration_request.$stamp.$safe"
    verdict = "PASS_APP_PACK_REGISTRATION_REQUEST_DRAFTED"
    kind = $Kind
    pack_id = $packId
    request = $requestPath.Replace($RepoRoot + '\','')
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    errors = @()
    warnings = @("not canonical registration")
  }

  $request | ConvertTo-Json -Depth 20 | Set-Content -Path $requestPath -Encoding UTF8
  $receipt | ConvertTo-Json -Depth 20 | Set-Content -Path $receiptPath -Encoding UTF8

  Add-Log "PACK_REQUEST_CREATED: $($requestPath.Replace($RepoRoot + '\',''))" "PASS"
  Add-Log "PACK_REQUEST_RECEIPT: $($receiptPath.Replace($RepoRoot + '\',''))" "PASS"
  Add-Log "Boundary: app-level request draft, not canonical registration." "AUTH"
  Refresh-Leveling
}

function Invoke-SelectedOrganAction {
  if ($script:OrganActionList.SelectedItems.Count -eq 0) {
    [System.Windows.Forms.MessageBox]::Show("Выбери функцию внутри органа.", "Imperium Launcher") | Out-Null
    return
  }

  $id = $script:OrganActionList.SelectedItems[0].Tag

  if ($id -eq "register-patch-pack") {
    $script:Tabs.SelectedTab = $script:TabPacks
    Register-PackRequest -Kind "PATCH_PACK"
    return
  }
  if ($id -eq "register-task-pack") {
    $script:Tabs.SelectedTab = $script:TabPacks
    Register-PackRequest -Kind "TASK_PACK"
    return
  }

  Invoke-TuiAction -ActionId $id
}

function Invoke-TuiAction {
  param([string]$ActionId)

  $a = $Actions | Where-Object { $_.id -eq $ActionId } | Select-Object -First 1
  if (-not $a) {
    Add-Log "Unknown TUI action: $ActionId" "ERROR"
    return
  }

  $script:CurrentAction = $a
  $script:CurrentTranscript.Clear() | Out-Null
  $script:RunButton.Enabled = $false

  Add-Log "============================================================" "AUTH"
  Add-Log "IMPERIUM LAUNCHER APP / AQUARIUM" "AUTH"
  Add-Log "============================================================" "AUTH"
  Add-Log "organ: $($script:CurrentOrgan.title)" "AUTH"
  Add-Log "action_id: $($a.id)" "AUTH"
  Add-Log "label: $($a.ru_label)" "AUTH"
  Add-Log "description: $($a.ru_description)"
  Add-Log "command: python SUPPORT/TUI/imperium_tui.py --repo-root <repo> --action $($a.id)"
  Add-Log "============================================================" "AUTH"

  $oldEncoding = $env:PYTHONIOENCODING
  $env:PYTHONIOENCODING = "utf-8"

  try {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "python"
    $psi.WorkingDirectory = $RepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
    $psi.ArgumentList.Add($ConsoleTui)
    $psi.ArgumentList.Add("--repo-root")
    $psi.ArgumentList.Add($RepoRoot)
    $psi.ArgumentList.Add("--action")
    $psi.ArgumentList.Add([string]$a.id)

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    Add-Log "----- terminal output begin -----"
    [void]$proc.Start()

    while (-not $proc.HasExited) {
      while (-not $proc.StandardOutput.EndOfStream) { Add-Log ($proc.StandardOutput.ReadLine()) }
      while (-not $proc.StandardError.EndOfStream) { Add-Log ("ERR: " + $proc.StandardError.ReadLine()) "ERROR" }
      Start-Sleep -Milliseconds 80
      [System.Windows.Forms.Application]::DoEvents()
    }

    while (-not $proc.StandardOutput.EndOfStream) { Add-Log ($proc.StandardOutput.ReadLine()) }
    while (-not $proc.StandardError.EndOfStream) { Add-Log ("ERR: " + $proc.StandardError.ReadLine()) "ERROR" }

    Add-Log "----- terminal output end -----"
    if ($proc.ExitCode -eq 0) { Add-Log "exit_code: 0" "PASS" } else { Add-Log "exit_code: $($proc.ExitCode)" "ERROR" }
    Save-AppTranscript -ActionId $a.id
    Refresh-Status
  }
  catch {
    Add-Log "APP_ERROR: $($_.Exception.Message)" "ERROR"
    Save-AppTranscript -ActionId $a.id
  }
  finally {
    $env:PYTHONIOENCODING = $oldEncoding
    $script:RunButton.Enabled = $true
  }
}

$Form = New-Object System.Windows.Forms.Form
$Form.Text = "Imperium Launcher — ORGAN HUB / LEVELING SYSTEM"
$Form.Width = 1560
$Form.Height = 940
$Form.StartPosition = "CenterScreen"
$Form.MinimumSize = New-Object System.Drawing.Size(1260,780)
$Form.BackColor = $C_Back
$Form.ForeColor = $C_Text

$Title = New-Object System.Windows.Forms.Label
$Title.Text = "IMPERIUM LEVELING SYSTEM"
$Title.Left = 18
$Title.Top = 10
$Title.Width = 520
$Title.Height = 34
$Title.Font = New-Object System.Drawing.Font("Consolas", 18, [System.Drawing.FontStyle]::Bold)
$Title.ForeColor = $C_Gold
$Form.Controls.Add($Title)

$LevelLabel = New-Object System.Windows.Forms.Label
$LevelLabel.Text = "LEVEL ?"
$LevelLabel.Left = 560
$LevelLabel.Top = 12
$LevelLabel.Width = 160
$LevelLabel.Height = 26
$LevelLabel.Font = New-Object System.Drawing.Font("Consolas", 14, [System.Drawing.FontStyle]::Bold)
$LevelLabel.ForeColor = $C_Purple
$Form.Controls.Add($LevelLabel)
$script:LevelLabel = $LevelLabel

$XPBar = New-Object System.Windows.Forms.ProgressBar
$XPBar.Left = 730
$XPBar.Top = 15
$XPBar.Width = 260
$XPBar.Height = 22
$XPBar.Minimum = 0
$XPBar.Maximum = 100
$Form.Controls.Add($XPBar)
$script:XPBar = $XPBar

$XPLabel = New-Object System.Windows.Forms.Label
$XPLabel.Text = "Proof XP: ?"
$XPLabel.Left = 1010
$XPLabel.Top = 14
$XPLabel.Width = 500
$XPLabel.Height = 24
$XPLabel.Font = New-Object System.Drawing.Font("Consolas", 10)
$XPLabel.ForeColor = $C_Cyan
$Form.Controls.Add($XPLabel)
$script:XPLabel = $XPLabel

$Tabs = New-Object System.Windows.Forms.TabControl
$Tabs.Left = 12
$Tabs.Top = 52
$Tabs.Width = 1518
$Tabs.Height = 825
$Tabs.Font = New-Object System.Drawing.Font("Consolas", 10)
$Form.Controls.Add($Tabs)
$script:Tabs = $Tabs

$TabHub = New-Object System.Windows.Forms.TabPage
$TabHub.Text = "ORGAN_HUB"
$TabHub.BackColor = $C_Panel
$Tabs.Controls.Add($TabHub)
$script:TabHub = $TabHub

$TabOrgan = New-Object System.Windows.Forms.TabPage
$TabOrgan.Text = "Орган"
$TabOrgan.BackColor = $C_Panel
$Tabs.Controls.Add($TabOrgan)
$script:TabOrgan = $TabOrgan

$TabPacks = New-Object System.Windows.Forms.TabPage
$TabPacks.Text = "PACK FORGE"
$TabPacks.BackColor = $C_Panel
$Tabs.Controls.Add($TabPacks)
$script:TabPacks = $TabPacks

$TabStatus = New-Object System.Windows.Forms.TabPage
$TabStatus.Text = "Статус"
$TabStatus.BackColor = $C_Panel
$Tabs.Controls.Add($TabStatus)

$TabLaw = New-Object System.Windows.Forms.TabPage
$TabLaw.Text = "Законы"
$TabLaw.BackColor = $C_Panel
$Tabs.Controls.Add($TabLaw)

# Hub
$HubLabel = New-Object System.Windows.Forms.Label
$HubLabel.Text = "Выбери орган. Функции появятся только после входа в орган."
$HubLabel.Left = 18
$HubLabel.Top = 14
$HubLabel.Width = 780
$HubLabel.Height = 25
$HubLabel.Font = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Bold)
$HubLabel.ForeColor = $C_Gold
$TabHub.Controls.Add($HubLabel)

$OrganList = New-Object System.Windows.Forms.ListView
$OrganList.Left = 18
$OrganList.Top = 50
$OrganList.Width = 650
$OrganList.Height = 520
$OrganList.View = "Details"
$OrganList.FullRowSelect = $true
$OrganList.GridLines = $true
$OrganList.BackColor = $C_PanelAlt
$OrganList.ForeColor = $C_Text
$OrganList.Font = New-Object System.Drawing.Font("Consolas", 11)
[void]$OrganList.Columns.Add("Орган", 170)
[void]$OrganList.Columns.Add("Профиль", 190)
[void]$OrganList.Columns.Add("Состояние", 260)
foreach ($room in $OrganRooms) {
  $item = New-Object System.Windows.Forms.ListViewItem($room.title)
  [void]$item.SubItems.Add($room.ru)
  [void]$item.SubItems.Add($room.status)
  $item.Tag = $room.id
  if (-not $room.unlocked) { $item.ForeColor = $C_Muted }
  [void]$OrganList.Items.Add($item)
}
$TabHub.Controls.Add($OrganList)
$script:OrganList = $OrganList

$XPDetailsBox = New-Object System.Windows.Forms.RichTextBox
$XPDetailsBox.Left = 690
$XPDetailsBox.Top = 50
$XPDetailsBox.Width = 790
$XPDetailsBox.Height = 520
$XPDetailsBox.ReadOnly = $true
$XPDetailsBox.BackColor = $C_PanelDeep
$XPDetailsBox.ForeColor = $C_Text
$XPDetailsBox.Font = New-Object System.Drawing.Font("Consolas", 11)
$TabHub.Controls.Add($XPDetailsBox)
$script:XPDetailsBox = $XPDetailsBox

$EnterOrganButton = New-Object System.Windows.Forms.Button
$EnterOrganButton.Text = "Войти в орган"
$EnterOrganButton.Left = 18
$EnterOrganButton.Top = 590
$EnterOrganButton.Width = 200
$EnterOrganButton.Height = 42
$EnterOrganButton.BackColor = $C_Gold
$EnterOrganButton.ForeColor = [System.Drawing.Color]::Black
$TabHub.Controls.Add($EnterOrganButton)

$RefreshLevelButton = New-Object System.Windows.Forms.Button
$RefreshLevelButton.Text = "Обновить уровень"
$RefreshLevelButton.Left = 235
$RefreshLevelButton.Top = 590
$RefreshLevelButton.Width = 220
$RefreshLevelButton.Height = 42
$TabHub.Controls.Add($RefreshLevelButton)

# Organ room
$OrganTitle = New-Object System.Windows.Forms.Label
$OrganTitle.Text = "ORGAN"
$OrganTitle.Left = 18
$OrganTitle.Top = 12
$OrganTitle.Width = 500
$OrganTitle.Height = 32
$OrganTitle.Font = New-Object System.Drawing.Font("Consolas", 17, [System.Drawing.FontStyle]::Bold)
$OrganTitle.ForeColor = $C_Gold
$TabOrgan.Controls.Add($OrganTitle)
$script:OrganTitle = $OrganTitle

$OrganSubtitle = New-Object System.Windows.Forms.Label
$OrganSubtitle.Text = "Выбери орган на главном экране."
$OrganSubtitle.Left = 530
$OrganSubtitle.Top = 18
$OrganSubtitle.Width = 780
$OrganSubtitle.Height = 24
$OrganSubtitle.Font = New-Object System.Drawing.Font("Consolas", 10)
$OrganSubtitle.ForeColor = $C_Muted
$TabOrgan.Controls.Add($OrganSubtitle)
$script:OrganSubtitle = $OrganSubtitle

$OrganActionList = New-Object System.Windows.Forms.ListView
$OrganActionList.Left = 18
$OrganActionList.Top = 58
$OrganActionList.Width = 650
$OrganActionList.Height = 430
$OrganActionList.View = "Details"
$OrganActionList.FullRowSelect = $true
$OrganActionList.GridLines = $true
$OrganActionList.BackColor = $C_PanelAlt
$OrganActionList.ForeColor = $C_Text
$OrganActionList.Font = New-Object System.Drawing.Font("Consolas", 10)
[void]$OrganActionList.Columns.Add("ID", 170)
[void]$OrganActionList.Columns.Add("Функция", 230)
[void]$OrganActionList.Columns.Add("Режим", 80)
[void]$OrganActionList.Columns.Add("Описание", 450)
$TabOrgan.Controls.Add($OrganActionList)
$script:OrganActionList = $OrganActionList

$DetailsBox = New-Object System.Windows.Forms.TextBox
$DetailsBox.Left = 18
$DetailsBox.Top = 505
$DetailsBox.Width = 650
$DetailsBox.Height = 150
$DetailsBox.Multiline = $true
$DetailsBox.ReadOnly = $true
$DetailsBox.ScrollBars = "Vertical"
$DetailsBox.BackColor = $C_PanelDeep
$DetailsBox.ForeColor = $C_Text
$DetailsBox.Font = New-Object System.Drawing.Font("Consolas", 10)
$TabOrgan.Controls.Add($DetailsBox)
$script:DetailsBox = $DetailsBox

$LogBox = New-Object System.Windows.Forms.RichTextBox
$LogBox.Left = 690
$LogBox.Top = 58
$LogBox.Width = 790
$LogBox.Height = 597
$LogBox.ReadOnly = $true
$LogBox.WordWrap = $false
$LogBox.ScrollBars = "Both"
$LogBox.BackColor = $C_LogBack
$LogBox.ForeColor = $C_LogText
$LogBox.Font = New-Object System.Drawing.Font("Consolas", 10)
$TabOrgan.Controls.Add($LogBox)
$script:LogBox = $LogBox

$RunButton = New-Object System.Windows.Forms.Button
$RunButton.Text = "Запустить функцию"
$RunButton.Left = 18
$RunButton.Top = 675
$RunButton.Width = 210
$RunButton.Height = 40
$RunButton.BackColor = $C_Gold
$RunButton.ForeColor = [System.Drawing.Color]::Black
$TabOrgan.Controls.Add($RunButton)
$script:RunButton = $RunButton

$BackHubButton = New-Object System.Windows.Forms.Button
$BackHubButton.Text = "Назад к органам"
$BackHubButton.Left = 245
$BackHubButton.Top = 675
$BackHubButton.Width = 190
$BackHubButton.Height = 40
$TabOrgan.Controls.Add($BackHubButton)

$CopyButton = New-Object System.Windows.Forms.Button
$CopyButton.Text = "Копировать лог"
$CopyButton.Left = 690
$CopyButton.Top = 675
$CopyButton.Width = 160
$CopyButton.Height = 40
$TabOrgan.Controls.Add($CopyButton)

$ClearButton = New-Object System.Windows.Forms.Button
$ClearButton.Text = "Очистить лог"
$ClearButton.Left = 860
$ClearButton.Top = 675
$ClearButton.Width = 150
$ClearButton.Height = 40
$TabOrgan.Controls.Add($ClearButton)

$SaveButton = New-Object System.Windows.Forms.Button
$SaveButton.Text = "Сохранить лог"
$SaveButton.Left = 1020
$SaveButton.Top = 675
$SaveButton.Width = 155
$SaveButton.Height = 40
$TabOrgan.Controls.Add($SaveButton)

$OpenLogsButton = New-Object System.Windows.Forms.Button
$OpenLogsButton.Text = "Открыть логи"
$OpenLogsButton.Left = 1185
$OpenLogsButton.Top = 675
$OpenLogsButton.Width = 150
$OpenLogsButton.Height = 40
$TabOrgan.Controls.Add($OpenLogsButton)

# Pack Forge
$PackTitle = New-Object System.Windows.Forms.Label
$PackTitle.Text = "PACK FORGE — заявки на регистрацию паков"
$PackTitle.Left = 18
$PackTitle.Top = 16
$PackTitle.Width = 650
$PackTitle.Height = 32
$PackTitle.Font = New-Object System.Drawing.Font("Consolas", 15, [System.Drawing.FontStyle]::Bold)
$PackTitle.ForeColor = $C_Gold
$TabPacks.Controls.Add($PackTitle)

$PackHint = New-Object System.Windows.Forms.Label
$PackHint.Text = "Пока это app-level request draft, не canonical registration. Позже подключим Astronomicon/Administratum registrar."
$PackHint.Left = 18
$PackHint.Top = 52
$PackHint.Width = 1100
$PackHint.Height = 24
$PackHint.Font = New-Object System.Drawing.Font("Consolas", 10)
$PackHint.ForeColor = $C_Muted
$TabPacks.Controls.Add($PackHint)

function Add-PackLabel($text, $x, $y) {
  $l = New-Object System.Windows.Forms.Label
  $l.Text = $text
  $l.Left = $x
  $l.Top = $y
  $l.Width = 180
  $l.Height = 22
  $l.ForeColor = $C_Text
  $l.Font = New-Object System.Drawing.Font("Consolas", 10)
  $TabPacks.Controls.Add($l)
}
Add-PackLabel "Pack ID" 18 100
$PackIdBox = New-Object System.Windows.Forms.TextBox
$PackIdBox.Left = 210
$PackIdBox.Top = 96
$PackIdBox.Width = 500
$PackIdBox.BackColor = $C_PanelDeep
$PackIdBox.ForeColor = $C_Text
$TabPacks.Controls.Add($PackIdBox)
$script:PackIdBox = $PackIdBox

Add-PackLabel "Название" 18 140
$PackTitleBox = New-Object System.Windows.Forms.TextBox
$PackTitleBox.Left = 210
$PackTitleBox.Top = 136
$PackTitleBox.Width = 500
$PackTitleBox.BackColor = $C_PanelDeep
$PackTitleBox.ForeColor = $C_Text
$TabPacks.Controls.Add($PackTitleBox)
$script:PackTitleBox = $PackTitleBox

Add-PackLabel "Орган" 18 180
$PackOrganBox = New-Object System.Windows.Forms.ComboBox
$PackOrganBox.Left = 210
$PackOrganBox.Top = 176
$PackOrganBox.Width = 280
$PackOrganBox.DropDownStyle = "DropDownList"
foreach ($x in @("ASTRONOMICON","CUSTODES","THRONE","ADMINISTRATUM","MECHANICUS","INQUISITION")) { [void]$PackOrganBox.Items.Add($x) }
$PackOrganBox.SelectedIndex = 0
$TabPacks.Controls.Add($PackOrganBox)
$script:PackOrganBox = $PackOrganBox

$PatchPackButton = New-Object System.Windows.Forms.Button
$PatchPackButton.Text = "Регистрация Patch Pack"
$PatchPackButton.Left = 210
$PatchPackButton.Top = 230
$PatchPackButton.Width = 260
$PatchPackButton.Height = 42
$PatchPackButton.BackColor = $C_Gold
$PatchPackButton.ForeColor = [System.Drawing.Color]::Black
$TabPacks.Controls.Add($PatchPackButton)

$TaskPackButton = New-Object System.Windows.Forms.Button
$TaskPackButton.Text = "Регистрация Task Pack"
$TaskPackButton.Left = 490
$TaskPackButton.Top = 230
$TaskPackButton.Width = 260
$TaskPackButton.Height = 42
$TabPacks.Controls.Add($TaskPackButton)

$PackLogHint = New-Object System.Windows.Forms.RichTextBox
$PackLogHint.Left = 18
$PackLogHint.Top = 300
$PackLogHint.Width = 980
$PackLogHint.Height = 300
$PackLogHint.ReadOnly = $true
$PackLogHint.BackColor = $C_PanelDeep
$PackLogHint.ForeColor = $C_Text
$PackLogHint.Font = New-Object System.Drawing.Font("Consolas", 11)
$PackLogHint.AppendText("PACK FORGE LAW" + [Environment]::NewLine + [Environment]::NewLine)
$PackLogHint.AppendText("- Patch Pack = Owner + Logos Prime manual/chat-agent patch." + [Environment]::NewLine)
$PackLogHint.AppendText("- Task Pack = Owner + Logos Prime + Servitor/external executor." + [Environment]::NewLine)
$PackLogHint.AppendText("- Эта форма создаёт request draft и receipt, не финальную каноническую регистрацию." + [Environment]::NewLine)
$PackLogHint.AppendText("- Все следы пишутся в SUPPORT/APP/REGISTRY/PACK_REQUESTS и SUPPORT/APP/RECEIPTS." + [Environment]::NewLine)
$TabPacks.Controls.Add($PackLogHint)

# Status
$StatusBox = New-Object System.Windows.Forms.RichTextBox
$StatusBox.Left = 18
$StatusBox.Top = 18
$StatusBox.Width = 1440
$StatusBox.Height = 690
$StatusBox.ReadOnly = $true
$StatusBox.BackColor = $C_LogBack
$StatusBox.ForeColor = $C_Text
$StatusBox.Font = New-Object System.Drawing.Font("Consolas", 11)
$TabStatus.Controls.Add($StatusBox)
$script:StatusBox = $StatusBox

# Laws
$LawBox = New-Object System.Windows.Forms.RichTextBox
$LawBox.Left = 18
$LawBox.Top = 18
$LawBox.Width = 1440
$LawBox.Height = 690
$LawBox.ReadOnly = $true
$LawBox.BackColor = $C_LogBack
$LawBox.ForeColor = $C_Text
$LawBox.Font = New-Object System.Drawing.Font("Consolas", 11)
$TabLaw.Controls.Add($LawBox)
$LawBox.AppendText("APP LAW" + [Environment]::NewLine + [Environment]::NewLine)
foreach ($law in $Manifest.new_ui_law) { $LawBox.AppendText("- $law" + [Environment]::NewLine) }
$LawBox.AppendText([Environment]::NewLine + "XP RULES" + [Environment]::NewLine + [Environment]::NewLine)
$LawBox.AppendText(($Manifest.xp_rules | ConvertTo-Json -Depth 10) + [Environment]::NewLine)
$LawBox.AppendText([Environment]::NewLine + "NOT CLAIMED" + [Environment]::NewLine + [Environment]::NewLine)
foreach ($x in $Manifest.not_claimed) { $LawBox.AppendText("- $x" + [Environment]::NewLine) }

$Footer = New-Object System.Windows.Forms.Label
$Footer.Text = "Imperium Launcher App v0.2 — organ hub, proof XP, clean streaks, pack request drafts, no hidden execution."
$Footer.Left = 18
$Footer.Top = 884
$Footer.Width = 1250
$Footer.Height = 24
$Footer.Font = New-Object System.Drawing.Font("Consolas", 9)
$Footer.ForeColor = $C_Muted
$Form.Controls.Add($Footer)

$EnterOrganButton.Add_Click({
  if ($script:OrganList.SelectedItems.Count -eq 0) {
    [System.Windows.Forms.MessageBox]::Show("Выбери орган.", "Organ Hub") | Out-Null
    return
  }
  $id = $script:OrganList.SelectedItems[0].Tag
  $room = $OrganRooms | Where-Object { $_.id -eq $id } | Select-Object -First 1
  Load-OrganRoom -Room $room
})
$OrganList.Add_DoubleClick({
  if ($script:OrganList.SelectedItems.Count -gt 0) {
    $id = $script:OrganList.SelectedItems[0].Tag
    $room = $OrganRooms | Where-Object { $_.id -eq $id } | Select-Object -First 1
    Load-OrganRoom -Room $room
  }
})
$RefreshLevelButton.Add_Click({ Refresh-Status; Add-Log "Leveling refreshed." "XP" })
$OrganActionList.Add_SelectedIndexChanged({ Update-OrganDetails })
$RunButton.Add_Click({ Invoke-SelectedOrganAction })
$BackHubButton.Add_Click({ $script:Tabs.SelectedTab = $script:TabHub })
$CopyButton.Add_Click({ if ($script:LogBox.TextLength -gt 0) { [System.Windows.Forms.Clipboard]::SetText($script:LogBox.Text); Add-Log "Log copied to clipboard." "PASS" } })
$ClearButton.Add_Click({ $script:LogBox.Clear(); $script:CurrentTranscript.Clear() | Out-Null })
$SaveButton.Add_Click({ $id = if ($script:CurrentAction) { $script:CurrentAction.id } else { "manual" }; Save-AppTranscript -ActionId $id })
$OpenLogsButton.Add_Click({ Start-Process explorer.exe $AppLogDir })
$PatchPackButton.Add_Click({ Register-PackRequest -Kind "PATCH_PACK" })
$TaskPackButton.Add_Click({ Register-PackRequest -Kind "TASK_PACK" })

if ($OrganList.Items.Count -gt 0) { $OrganList.Items[0].Selected = $true }
Refresh-Status
Add-Log "Imperium Launcher App v0.2 started: ORGAN_HUB / IMPERIUM LEVELING SYSTEM." "AUTH"
Add-Log "Enter an organ to reveal its functions. Aquarium output stays visible in organ room." "AUTH"

[void]$Form.ShowDialog()
