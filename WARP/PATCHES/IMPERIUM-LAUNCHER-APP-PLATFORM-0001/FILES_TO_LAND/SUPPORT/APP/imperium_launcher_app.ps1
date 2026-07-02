param(
  [switch]$SelfTest
)

$ErrorActionPreference = "Stop"

function Write-JsonAndExit {
  param([hashtable]$Data, [int]$Code)
  $Data | ConvertTo-Json -Depth 30
  exit $Code
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$AppRoot = $PSScriptRoot
$ManifestPath = Join-Path $RepoRoot "SUPPORT\APP\IMPERIUM_LAUNCHER_APP_MANIFEST_V0_1.json"
$ThemePath = Join-Path $RepoRoot "SUPPORT\APP\IMPERIUM_APP_THEME_V0_1.json"
$ActionsPath = Join-Path $RepoRoot "SUPPORT\TUI\IMPERIUM_TUI_ACTIONS_V0_1.json"
$ConsoleTui = Join-Path $RepoRoot "SUPPORT\TUI\imperium_tui.py"
$AppLogDir = Join-Path $RepoRoot "SUPPORT\APP\LOGS"
$TuiLogDir = Join-Path $RepoRoot "SUPPORT\TUI\LOGS"
$TuiReceiptDir = Join-Path $RepoRoot "SUPPORT\TUI\RECEIPTS"

function Read-Json($Path) {
  if (-not (Test-Path $Path)) { return $null }
  return Get-Content $Path -Raw | ConvertFrom-Json
}

$Manifest = Read-Json $ManifestPath
$Theme = Read-Json $ThemePath
$ActionsManifest = Read-Json $ActionsPath
$Actions = @()
if ($ActionsManifest -and $ActionsManifest.actions) {
  $Actions = @($ActionsManifest.actions)
}

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
    "System.Windows.Forms",
    "TabControl",
    "RichTextBox",
    "ListView",
    "Запустить функцию",
    "Копировать лог",
    "Очистить лог",
    "Открыть логи",
    "Астрономикон",
    "Кустодес",
    "Трон",
    "CROWN_AWARE_OVERLAY",
    "Invoke-AppAction",
    "Refresh-Status"
  )) {
    if ($scriptText -notlike "*$needle*") { $errors.Add("missing app marker: $needle") }
  }

  $verdict = if ($errors.Count -eq 0) { "PASS_IMPERIUM_LAUNCHER_APP_PLATFORM_SELFTEST" } else { "FAIL_IMPERIUM_LAUNCHER_APP_PLATFORM_SELFTEST" }
  $code = if ($errors.Count -eq 0) { 0 } else { 1 }

  Write-JsonAndExit @{
    task_id = "IMPERIUM-LAUNCHER-APP-PLATFORM-0001"
    validator_id = "imperium_launcher_app_platform_selftest.v0_1"
    verdict = $verdict
    action_count = $Actions.Count
    app_id = if ($Manifest) { $Manifest.app_id } else { $null }
    theme_id = if ($Theme) { $Theme.theme_id } else { $null }
    errors = @($errors)
    warnings = @()
  } $code
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

New-Item -ItemType Directory -Force -Path $AppLogDir | Out-Null
New-Item -ItemType Directory -Force -Path $TuiLogDir | Out-Null
New-Item -ItemType Directory -Force -Path $TuiReceiptDir | Out-Null

function ColorFromHex([string]$hex, [string]$fallback) {
  if ([string]::IsNullOrWhiteSpace($hex)) { $hex = $fallback }
  return [System.Drawing.ColorTranslator]::FromHtml($hex)
}

$Colors = $Theme.colors
$C_Back = ColorFromHex $Colors.background "#0B0B0F"
$C_Panel = ColorFromHex $Colors.panel "#15151D"
$C_PanelAlt = ColorFromHex $Colors.panel_alt "#1D1A24"
$C_Text = ColorFromHex $Colors.text "#E6E0C8"
$C_Muted = ColorFromHex $Colors.muted "#9B9275"
$C_Gold = ColorFromHex $Colors.gold "#D6B45A"
$C_Purple = ColorFromHex $Colors.purple "#6C3DD1"
$C_Red = ColorFromHex $Colors.red "#A64040"
$C_Green = ColorFromHex $Colors.green "#5DAA67"
$C_LogBack = ColorFromHex $Colors.log_background "#050507"
$C_LogText = ColorFromHex $Colors.log_text "#D7D7D7"

$script:CurrentAction = $null
$script:CurrentTranscript = New-Object System.Text.StringBuilder

function Add-Log {
  param([string]$Text, [string]$Level = "INFO")
  $timestamp = (Get-Date).ToString("HH:mm:ss")
  $line = "[$timestamp][$Level] $Text"
  $script:LogBox.SelectionStart = $script:LogBox.TextLength
  if ($Level -eq "ERROR") { $script:LogBox.SelectionColor = $C_Red }
  elseif ($Level -eq "PASS") { $script:LogBox.SelectionColor = $C_Green }
  elseif ($Level -eq "AUTH") { $script:LogBox.SelectionColor = $C_Gold }
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

function Refresh-Status {
  $readout = Get-Json "ORGANS\THRONE\REPORTS\POST_ASTRONOMICON_SCORE_READOUT_SUMMARY_V0_1.json"
  $throne = Get-Json "ORGANS\THRONE\REPORTS\THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json"
  $custodes = Get-Json "ORGANS\CUSTODES\REPORTS\CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json"

  $script:StatusBox.Clear()
  $script:StatusBox.SelectionColor = $C_Gold
  $script:StatusBox.AppendText("IMPERIUM LAUNCHER APP / STATUS" + [Environment]::NewLine)
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
      $script:StatusBox.AppendText("red_team_score: $(Format-Value $c.red_team_score)" + [Environment]::NewLine)
      $script:StatusBox.AppendText("blue_team_score: $(Format-Value $c.blue_team_score)" + [Environment]::NewLine)
      $script:StatusBox.AppendText("custodes_organ_validators_score: $(Format-Value $c.custodes_organ_validators_score)" + [Environment]::NewLine)
      $script:StatusBox.AppendText("throne_organ_validators_score: $(Format-Value $c.throne_organ_validators_score)" + [Environment]::NewLine)
      $script:StatusBox.AppendText("trust_proven_score: $(Format-Value $c.trust_proven_score)" + [Environment]::NewLine)
      $script:StatusBox.AppendText("rule_validated_score: $(Format-Value $c.rule_validated_score)" + [Environment]::NewLine)
      $script:StatusBox.AppendText("organ_truth_maturity_score_crown_aware_estimate: $(Format-Value $c.organ_truth_maturity_score_crown_aware_estimate)" + [Environment]::NewLine)
      $script:StatusBox.AppendText("organ_assembled_score: $(Format-Value $c.organ_assembled_score)" + [Environment]::NewLine)
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
}

function Update-Details {
  if ($script:ActionList.SelectedItems.Count -eq 0) { return }
  $id = $script:ActionList.SelectedItems[0].Tag
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

function Invoke-AppAction {
  if ($script:ActionList.SelectedItems.Count -eq 0) {
    [System.Windows.Forms.MessageBox]::Show("Выбери функцию.", "Imperium Launcher") | Out-Null
    return
  }

  $id = $script:ActionList.SelectedItems[0].Tag
  $a = $Actions | Where-Object { $_.id -eq $id } | Select-Object -First 1
  if (-not $a) { return }

  $script:CurrentAction = $a
  $script:CurrentTranscript.Clear() | Out-Null
  $script:RunButton.Enabled = $false

  Add-Log "============================================================" "AUTH"
  Add-Log "IMPERIUM LAUNCHER APP / AQUARIUM" "AUTH"
  Add-Log "============================================================" "AUTH"
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
      while (-not $proc.StandardOutput.EndOfStream) {
        Add-Log ($proc.StandardOutput.ReadLine())
      }
      while (-not $proc.StandardError.EndOfStream) {
        Add-Log ("ERR: " + $proc.StandardError.ReadLine()) "ERROR"
      }
      Start-Sleep -Milliseconds 80
      [System.Windows.Forms.Application]::DoEvents()
    }

    while (-not $proc.StandardOutput.EndOfStream) {
      Add-Log ($proc.StandardOutput.ReadLine())
    }
    while (-not $proc.StandardError.EndOfStream) {
      Add-Log ("ERR: " + $proc.StandardError.ReadLine()) "ERROR"
    }

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
$Form.Text = "Imperium Launcher — App Platform — Astronomicon / Custodes / Throne"
$Form.Width = 1480
$Form.Height = 900
$Form.StartPosition = "CenterScreen"
$Form.MinimumSize = New-Object System.Drawing.Size(1200,760)
$Form.BackColor = $C_Back
$Form.ForeColor = $C_Text

$Title = New-Object System.Windows.Forms.Label
$Title.Text = "IMPERIUM LAUNCHER"
$Title.Left = 16
$Title.Top = 12
$Title.Width = 440
$Title.Height = 34
$Title.Font = New-Object System.Drawing.Font("Consolas", 18, [System.Drawing.FontStyle]::Bold)
$Title.ForeColor = $C_Gold
$Form.Controls.Add($Title)

$SubTitle = New-Object System.Windows.Forms.Label
$SubTitle.Text = "Платформа приложения: функции, органы, аквариум, Crown-aware status"
$SubTitle.Left = 460
$SubTitle.Top = 18
$SubTitle.Width = 900
$SubTitle.Height = 24
$SubTitle.Font = New-Object System.Drawing.Font("Consolas", 10)
$SubTitle.ForeColor = $C_Muted
$Form.Controls.Add($SubTitle)

$Tabs = New-Object System.Windows.Forms.TabControl
$Tabs.Left = 12
$Tabs.Top = 55
$Tabs.Width = 1435
$Tabs.Height = 765
$Tabs.Font = New-Object System.Drawing.Font("Consolas", 10)
$Form.Controls.Add($Tabs)

$TabOps = New-Object System.Windows.Forms.TabPage
$TabOps.Text = "Пульт"
$TabOps.BackColor = $C_Panel
$Tabs.Controls.Add($TabOps)

$TabStatus = New-Object System.Windows.Forms.TabPage
$TabStatus.Text = "Статус"
$TabStatus.BackColor = $C_Panel
$Tabs.Controls.Add($TabStatus)

$TabLaw = New-Object System.Windows.Forms.TabPage
$TabLaw.Text = "Законы"
$TabLaw.BackColor = $C_Panel
$Tabs.Controls.Add($TabLaw)

$ActionList = New-Object System.Windows.Forms.ListView
$ActionList.Left = 12
$ActionList.Top = 12
$ActionList.Width = 540
$ActionList.Height = 430
$ActionList.View = "Details"
$ActionList.FullRowSelect = $true
$ActionList.GridLines = $true
$ActionList.BackColor = $C_PanelAlt
$ActionList.ForeColor = $C_Text
$ActionList.Font = New-Object System.Drawing.Font("Consolas", 9)
[void]$ActionList.Columns.Add("ID", 170)
[void]$ActionList.Columns.Add("Функция", 250)
[void]$ActionList.Columns.Add("Режим", 100)
foreach ($a in $Actions) {
  $item = New-Object System.Windows.Forms.ListViewItem([string]$a.id)
  [void]$item.SubItems.Add([string]$a.ru_label)
  $mode = if ($a.mutates_repo) { "writes" } else { "read" }
  [void]$item.SubItems.Add($mode)
  $item.Tag = [string]$a.id
  [void]$ActionList.Items.Add($item)
}
$TabOps.Controls.Add($ActionList)
$script:ActionList = $ActionList

$DetailsBox = New-Object System.Windows.Forms.TextBox
$DetailsBox.Left = 12
$DetailsBox.Top = 455
$DetailsBox.Width = 540
$DetailsBox.Height = 210
$DetailsBox.Multiline = $true
$DetailsBox.ReadOnly = $true
$DetailsBox.ScrollBars = "Vertical"
$DetailsBox.BackColor = $C_PanelAlt
$DetailsBox.ForeColor = $C_Text
$DetailsBox.Font = New-Object System.Drawing.Font("Consolas", 10)
$TabOps.Controls.Add($DetailsBox)
$script:DetailsBox = $DetailsBox

$LogBox = New-Object System.Windows.Forms.RichTextBox
$LogBox.Left = 570
$LogBox.Top = 12
$LogBox.Width = 835
$LogBox.Height = 653
$LogBox.ReadOnly = $true
$LogBox.WordWrap = $false
$LogBox.ScrollBars = "Both"
$LogBox.BackColor = $C_LogBack
$LogBox.ForeColor = $C_LogText
$LogBox.Font = New-Object System.Drawing.Font("Consolas", 10)
$TabOps.Controls.Add($LogBox)
$script:LogBox = $LogBox

$RunButton = New-Object System.Windows.Forms.Button
$RunButton.Text = "Запустить функцию"
$RunButton.Left = 12
$RunButton.Top = 680
$RunButton.Width = 190
$RunButton.Height = 36
$RunButton.BackColor = $C_Gold
$RunButton.ForeColor = [System.Drawing.Color]::Black
$TabOps.Controls.Add($RunButton)
$script:RunButton = $RunButton

$CopyButton = New-Object System.Windows.Forms.Button
$CopyButton.Text = "Копировать лог"
$CopyButton.Left = 570
$CopyButton.Top = 680
$CopyButton.Width = 155
$CopyButton.Height = 36
$TabOps.Controls.Add($CopyButton)

$ClearButton = New-Object System.Windows.Forms.Button
$ClearButton.Text = "Очистить лог"
$ClearButton.Left = 735
$ClearButton.Top = 680
$ClearButton.Width = 145
$ClearButton.Height = 36
$TabOps.Controls.Add($ClearButton)

$SaveButton = New-Object System.Windows.Forms.Button
$SaveButton.Text = "Сохранить лог"
$SaveButton.Left = 890
$SaveButton.Top = 680
$SaveButton.Width = 150
$SaveButton.Height = 36
$TabOps.Controls.Add($SaveButton)

$OpenLogsButton = New-Object System.Windows.Forms.Button
$OpenLogsButton.Text = "Открыть логи"
$OpenLogsButton.Left = 1050
$OpenLogsButton.Top = 680
$OpenLogsButton.Width = 140
$OpenLogsButton.Height = 36
$TabOps.Controls.Add($OpenLogsButton)

$RefreshButton = New-Object System.Windows.Forms.Button
$RefreshButton.Text = "Обновить статус"
$RefreshButton.Left = 210
$RefreshButton.Top = 680
$RefreshButton.Width = 170
$RefreshButton.Height = 36
$TabOps.Controls.Add($RefreshButton)

$StatusBox = New-Object System.Windows.Forms.RichTextBox
$StatusBox.Left = 12
$StatusBox.Top = 12
$StatusBox.Width = 1388
$StatusBox.Height = 690
$StatusBox.ReadOnly = $true
$StatusBox.BackColor = $C_LogBack
$StatusBox.ForeColor = $C_Text
$StatusBox.Font = New-Object System.Drawing.Font("Consolas", 11)
$TabStatus.Controls.Add($StatusBox)
$script:StatusBox = $StatusBox

$LawBox = New-Object System.Windows.Forms.RichTextBox
$LawBox.Left = 12
$LawBox.Top = 12
$LawBox.Width = 1388
$LawBox.Height = 690
$LawBox.ReadOnly = $true
$LawBox.BackColor = $C_LogBack
$LawBox.ForeColor = $C_Text
$LawBox.Font = New-Object System.Drawing.Font("Consolas", 11)
$TabLaw.Controls.Add($LawBox)
$LawBox.AppendText("APP LAW" + [Environment]::NewLine + [Environment]::NewLine)
foreach ($law in $Manifest.app_law) {
  $LawBox.AppendText("- $law" + [Environment]::NewLine)
}
$LawBox.AppendText([Environment]::NewLine + "NOT CLAIMED" + [Environment]::NewLine + [Environment]::NewLine)
foreach ($x in $Manifest.not_claimed) {
  $LawBox.AppendText("- $x" + [Environment]::NewLine)
}

$Footer = New-Object System.Windows.Forms.Label
$Footer.Text = "Imperium Launcher App v0.1 — no git land, no hidden execution, no Throne self-validation claim."
$Footer.Left = 16
$Footer.Top = 830
$Footer.Width = 1100
$Footer.Height = 24
$Footer.Font = New-Object System.Drawing.Font("Consolas", 9)
$Footer.ForeColor = $C_Muted
$Form.Controls.Add($Footer)

$ActionList.Add_SelectedIndexChanged({ Update-Details })
$RunButton.Add_Click({ Invoke-AppAction })
$RefreshButton.Add_Click({ Refresh-Status; Add-Log "Status refreshed." "PASS" })
$CopyButton.Add_Click({
  if ($script:LogBox.TextLength -gt 0) {
    [System.Windows.Forms.Clipboard]::SetText($script:LogBox.Text)
    Add-Log "Log copied to clipboard." "PASS"
  }
})
$ClearButton.Add_Click({
  $script:LogBox.Clear()
  $script:CurrentTranscript.Clear() | Out-Null
})
$SaveButton.Add_Click({
  $id = if ($script:CurrentAction) { $script:CurrentAction.id } else { "manual" }
  Save-AppTranscript -ActionId $id
})
$OpenLogsButton.Add_Click({
  Start-Process explorer.exe $AppLogDir
})

if ($ActionList.Items.Count -gt 0) {
  $ActionList.Items[0].Selected = $true
  Update-Details
}
Refresh-Status
Add-Log "Imperium Launcher App started." "AUTH"
Add-Log "Select function and press 'Запустить функцию'. Aquarium output stays visible here." "AUTH"

[void]$Form.ShowDialog()
