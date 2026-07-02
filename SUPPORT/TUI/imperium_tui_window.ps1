param(
  [switch]$SelfTest
)

$ErrorActionPreference = "Stop"

function Write-JsonAndExit([hashtable]$Data, [int]$Code) {
  $Data | ConvertTo-Json -Depth 20
  exit $Code
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ActionsPath = Join-Path $RepoRoot "SUPPORT\TUI\IMPERIUM_TUI_ACTIONS_V0_1.json"
$ConsoleTui = Join-Path $RepoRoot "SUPPORT\TUI\imperium_tui.py"
$LogDir = Join-Path $RepoRoot "SUPPORT\TUI\LOGS"
$ReceiptDir = Join-Path $RepoRoot "SUPPORT\TUI\RECEIPTS"

if (-not (Test-Path $ActionsPath)) {
  Write-JsonAndExit @{
    verdict = "FAIL_IMPERIUM_TUI_WINDOWED_AQUARIUM_SELFTEST"
    errors = @("actions manifest missing: $ActionsPath")
  } 1
}

$ActionsManifest = Get-Content $ActionsPath -Raw | ConvertFrom-Json
$Actions = @($ActionsManifest.actions)

if ($SelfTest) {
  $errors = New-Object System.Collections.Generic.List[string]
  if ($Actions.Count -lt 8) { $errors.Add("action count below threshold") }
  foreach ($a in $Actions) {
    if ([string]::IsNullOrWhiteSpace($a.ru_label)) { $errors.Add("missing ru_label: $($a.id)") }
    if ([string]::IsNullOrWhiteSpace($a.ru_description)) { $errors.Add("missing ru_description: $($a.id)") }
    if ($a.aquarium_log_required -ne $true) { $errors.Add("aquarium not required: $($a.id)") }
  }
  if (-not (Test-Path $ConsoleTui)) { $errors.Add("console TUI missing: $ConsoleTui") }

  try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
  } catch {
    $errors.Add("cannot load Windows Forms: $($_.Exception.Message)")
  }

  $scriptText = Get-Content $PSCommandPath -Raw
  foreach ($needle in @("RichTextBox", "Копировать лог", "Очистить лог", "Открыть папку логов", "Выполнить", "Clipboard")) {
    if ($scriptText -notlike "*$needle*") { $errors.Add("missing UI marker: $needle") }
  }

  $verdict = if ($errors.Count -eq 0) { "PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_SELFTEST" } else { "FAIL_IMPERIUM_TUI_WINDOWED_AQUARIUM_SELFTEST" }
  Write-JsonAndExit @{
    task_id = "IMPERIUM-TUI-WINDOWED-AQUARIUM-LAUNCHER-0001"
    validator_id = "imperium_tui_windowed_aquarium_selftest.v0_1"
    verdict = $verdict
    action_count = $Actions.Count
    errors = @($errors)
    warnings = @()
  } ($(if ($errors.Count -eq 0) {0} else {1}))
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $ReceiptDir | Out-Null

$script:CurrentAction = $null
$script:CurrentTranscript = New-Object System.Text.StringBuilder

function Add-Log {
  param([string]$Text)
  $timestamp = (Get-Date).ToString("HH:mm:ss")
  $line = "[$timestamp] $Text"
  $script:LogBox.AppendText($line + [Environment]::NewLine)
  $script:LogBox.SelectionStart = $script:LogBox.TextLength
  $script:LogBox.ScrollToCaret()
  [void]$script:CurrentTranscript.AppendLine($line)
  [System.Windows.Forms.Application]::DoEvents()
}

function Save-WindowTranscript {
  param([string]$ActionId)
  if ([string]::IsNullOrWhiteSpace($ActionId)) { $ActionId = "window" }
  $stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
  $safe = ($ActionId -replace '[^A-Za-z0-9_.-]+', '_')
  $path = Join-Path $LogDir "${stamp}_window_${safe}.log"
  $script:CurrentTranscript.ToString() | Set-Content -Path $path -Encoding UTF8
  Add-Log "WINDOW_LOG_SAVED: $($path.Replace($RepoRoot + '\',''))"
}

function Invoke-TuiAction {
  param([object]$Action)

  $script:CurrentAction = $Action
  $script:CurrentTranscript.Clear() | Out-Null

  Add-Log "============================================================"
  Add-Log "IMPERIUM WINDOWED TUI / АКВАРИУМ ОКНА"
  Add-Log "============================================================"
  Add-Log "repo: $RepoRoot"
  Add-Log "action_id: $($Action.id)"
  Add-Log "label: $($Action.ru_label)"
  Add-Log "description: $($Action.ru_description)"
  Add-Log "mutates_repo: $($Action.mutates_repo)"
  Add-Log "underlying command:"
  Add-Log "python SUPPORT/TUI/imperium_tui.py --repo-root <repo> --action $($Action.id)"
  Add-Log "============================================================"

  $script:RunButton.Enabled = $false
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
    $psi.ArgumentList.Add([string]$Action.id)

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    Add-Log "----- terminal output begin -----"
    [void]$proc.Start()

    while (-not $proc.HasExited) {
      while (-not $proc.StandardOutput.EndOfStream) {
        Add-Log ($proc.StandardOutput.ReadLine())
      }
      while (-not $proc.StandardError.EndOfStream) {
        Add-Log ("ERR: " + $proc.StandardError.ReadLine())
      }
      Start-Sleep -Milliseconds 80
      [System.Windows.Forms.Application]::DoEvents()
    }

    while (-not $proc.StandardOutput.EndOfStream) {
      Add-Log ($proc.StandardOutput.ReadLine())
    }
    while (-not $proc.StandardError.EndOfStream) {
      Add-Log ("ERR: " + $proc.StandardError.ReadLine())
    }

    Add-Log "----- terminal output end -----"
    Add-Log "exit_code: $($proc.ExitCode)"
    Save-WindowTranscript -ActionId $Action.id
  }
  catch {
    Add-Log "WINDOW_TUI_ERROR: $($_.Exception.Message)"
    Save-WindowTranscript -ActionId $Action.id
  }
  finally {
    $env:PYTHONIOENCODING = $oldEncoding
    $script:RunButton.Enabled = $true
  }
}

function Update-Details {
  $idx = $script:ListBox.SelectedIndex
  if ($idx -lt 0) { return }
  $a = $Actions[$idx]
  $script:DetailsBox.Text = @"
ID: $($a.id)

Функция:
$($a.ru_label)

Что делает:
$($a.ru_description)

Пишет repo:
$($a.mutates_repo)

Аквариум:
$($a.aquarium_log_required)

Тип:
$($a.kind)
"@
}

$Form = New-Object System.Windows.Forms.Form
$Form.Text = "Империум TUI — Астрономикон / Кустодес / Трон — Аквариум"
$Form.Width = 1320
$Form.Height = 840
$Form.StartPosition = "CenterScreen"
$Form.MinimumSize = New-Object System.Drawing.Size(1100,700)

$Header = New-Object System.Windows.Forms.Label
$Header.Text = "Империум TUI: функции слева, аквариум работы справа. Лог можно копировать и очищать."
$Header.Left = 10
$Header.Top = 10
$Header.Width = 1260
$Header.Height = 24
$Header.Font = New-Object System.Drawing.Font("Consolas", 10, [System.Drawing.FontStyle]::Bold)
$Form.Controls.Add($Header)

$ListBox = New-Object System.Windows.Forms.ListBox
$ListBox.Left = 10
$ListBox.Top = 45
$ListBox.Width = 410
$ListBox.Height = 360
$ListBox.Font = New-Object System.Drawing.Font("Consolas", 10)
foreach ($a in $Actions) {
  [void]$ListBox.Items.Add("$($a.id) — $($a.ru_label)")
}
$Form.Controls.Add($ListBox)
$script:ListBox = $ListBox

$DetailsBox = New-Object System.Windows.Forms.TextBox
$DetailsBox.Left = 10
$DetailsBox.Top = 415
$DetailsBox.Width = 410
$DetailsBox.Height = 260
$DetailsBox.Multiline = $true
$DetailsBox.ReadOnly = $true
$DetailsBox.ScrollBars = "Vertical"
$DetailsBox.Font = New-Object System.Drawing.Font("Consolas", 10)
$Form.Controls.Add($DetailsBox)
$script:DetailsBox = $DetailsBox

$RunButton = New-Object System.Windows.Forms.Button
$RunButton.Text = "Выполнить функцию"
$RunButton.Left = 10
$RunButton.Top = 690
$RunButton.Width = 190
$RunButton.Height = 34
$Form.Controls.Add($RunButton)
$script:RunButton = $RunButton

$ExitButton = New-Object System.Windows.Forms.Button
$ExitButton.Text = "Закрыть"
$ExitButton.Left = 230
$ExitButton.Top = 690
$ExitButton.Width = 190
$ExitButton.Height = 34
$Form.Controls.Add($ExitButton)

$LogBox = New-Object System.Windows.Forms.RichTextBox
$LogBox.Left = 440
$LogBox.Top = 45
$LogBox.Width = 840
$LogBox.Height = 630
$LogBox.ReadOnly = $true
$LogBox.WordWrap = $false
$LogBox.ScrollBars = "Both"
$LogBox.Font = New-Object System.Drawing.Font("Consolas", 10)
$LogBox.BackColor = [System.Drawing.Color]::FromArgb(12,12,12)
$LogBox.ForeColor = [System.Drawing.Color]::Gainsboro
$Form.Controls.Add($LogBox)
$script:LogBox = $LogBox

$CopyButton = New-Object System.Windows.Forms.Button
$CopyButton.Text = "Копировать лог"
$CopyButton.Left = 440
$CopyButton.Top = 690
$CopyButton.Width = 160
$CopyButton.Height = 34
$Form.Controls.Add($CopyButton)

$ClearButton = New-Object System.Windows.Forms.Button
$ClearButton.Text = "Очистить лог"
$ClearButton.Left = 610
$ClearButton.Top = 690
$ClearButton.Width = 150
$ClearButton.Height = 34
$Form.Controls.Add($ClearButton)

$SaveButton = New-Object System.Windows.Forms.Button
$SaveButton.Text = "Сохранить окно"
$SaveButton.Left = 770
$SaveButton.Top = 690
$SaveButton.Width = 160
$SaveButton.Height = 34
$Form.Controls.Add($SaveButton)

$OpenLogsButton = New-Object System.Windows.Forms.Button
$OpenLogsButton.Text = "Открыть папку логов"
$OpenLogsButton.Left = 940
$OpenLogsButton.Top = 690
$OpenLogsButton.Width = 180
$OpenLogsButton.Height = 34
$Form.Controls.Add($OpenLogsButton)

$StatusLabel = New-Object System.Windows.Forms.Label
$StatusLabel.Text = "Готово. Выбери функцию слева и нажми Выполнить."
$StatusLabel.Left = 440
$StatusLabel.Top = 735
$StatusLabel.Width = 820
$StatusLabel.Height = 26
$StatusLabel.Font = New-Object System.Drawing.Font("Consolas", 10)
$Form.Controls.Add($StatusLabel)

$ListBox.Add_SelectedIndexChanged({ Update-Details })

$RunButton.Add_Click({
  if ($script:ListBox.SelectedIndex -lt 0) {
    [System.Windows.Forms.MessageBox]::Show("Выбери функцию слева.", "Imperium TUI") | Out-Null
    return
  }
  $a = $Actions[$script:ListBox.SelectedIndex]
  Invoke-TuiAction -Action $a
})

$CopyButton.Add_Click({
  if ($script:LogBox.TextLength -gt 0) {
    [System.Windows.Forms.Clipboard]::SetText($script:LogBox.Text)
    $StatusLabel.Text = "Лог скопирован в буфер обмена."
  }
})

$ClearButton.Add_Click({
  $script:LogBox.Clear()
  $script:CurrentTranscript.Clear() | Out-Null
  $StatusLabel.Text = "Окно лога очищено."
})

$SaveButton.Add_Click({
  $id = if ($script:CurrentAction) { $script:CurrentAction.id } else { "manual" }
  Save-WindowTranscript -ActionId $id
  $StatusLabel.Text = "Окно лога сохранено."
})

$OpenLogsButton.Add_Click({
  Start-Process explorer.exe $LogDir
})

$ExitButton.Add_Click({ $Form.Close() })

if ($Actions.Count -gt 0) {
  $ListBox.SelectedIndex = 0
  Update-Details
}

Add-Log "Окно аквариума запущено."
Add-Log "Выбери функцию слева. Лог каждой функции будет виден здесь, плюс сохранится в SUPPORT/TUI/LOGS."

[void]$Form.ShowDialog()
