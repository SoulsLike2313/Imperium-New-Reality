param(
  [Parameter(Mandatory=$true)][string]$ReportRoot,
  [Parameter(Mandatory=$true)][string]$RawDir
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Continue'

function Invoke-Record {
  param(
    [string]$Id,
    [string]$Command
  )
  $outFile = Join-Path $RawDir ("$Id.txt")
  $start = (Get-Date).ToUniversalTime().ToString('o')
  $stdout = ''
  $stderr = ''
  $exitCode = 0
  try {
    $all = & cmd /c $Command 2>&1
    $exitCode = $LASTEXITCODE
    if($all){
      $stdout = ($all | Out-String)
    }
  } catch {
    $exitCode = 1
    $stderr = $_.Exception.Message
  }
  $end = (Get-Date).ToUniversalTime().ToString('o')
  $body = @(
    "id: $Id",
    "command: $Command",
    "started_at_utc: $start",
    "finished_at_utc: $end",
    "exit_code: $exitCode",
    '--- stdout/stderr ---',
    $stdout,
    $stderr
  ) -join "`r`n"
  Set-Content -LiteralPath $outFile -Value $body -Encoding utf8
  [ordered]@{
    id=$Id
    command=$Command
    started_at_utc=$start
    finished_at_utc=$end
    exit_code=$exitCode
    output_file=$outFile
    output_preview=((($stdout + "`n" + $stderr).Trim()) -replace "\r?\n", ' ')
  }
}

$checks = @(
  @{ id='winget_where'; cmd='where winget' },
  @{ id='winget_version'; cmd='winget --version' },
  @{ id='winget_source_list'; cmd='winget source list' },
  @{ id='node_where'; cmd='where node' },
  @{ id='node_version'; cmd='node --version' },
  @{ id='npm_where'; cmd='where npm' },
  @{ id='npm_version'; cmd='npm --version' },
  @{ id='npm_prefix'; cmd='npm config get prefix' },
  @{ id='py_where'; cmd='where py' },
  @{ id='py_version'; cmd='py -V' },
  @{ id='py_pip_version'; cmd='py -m pip --version' },
  @{ id='python_where'; cmd='where python' },
  @{ id='python_version'; cmd='python --version' },
  @{ id='python_pip_version'; cmd='python -m pip --version' },
  @{ id='python_user_base'; cmd='python -m site --user-base' },
  @{ id='python_user_site'; cmd='python -m site --user-site' },
  @{ id='tool_7z_where'; cmd='where 7z' },
  @{ id='tool_7z_info'; cmd='7z i' },
  @{ id='tool_markdownlint_where'; cmd='where markdownlint' },
  @{ id='tool_markdownlint_version'; cmd='markdownlint --version' },
  @{ id='tool_check_jsonschema_where'; cmd='where check-jsonschema' },
  @{ id='tool_check_jsonschema_version'; cmd='check-jsonschema --version' },
  @{ id='tool_python_module_check_jsonschema_version'; cmd='python -m check_jsonschema --version' },
  @{ id='tool_yamllint_where'; cmd='where yamllint' },
  @{ id='tool_yamllint_version'; cmd='yamllint --version' },
  @{ id='tool_python_module_yamllint_version'; cmd='python -m yamllint --version' }
)

$results = @()
foreach($c in $checks){
  $results += Invoke-Record -Id $c.id -Command $c.cmd
}

$pf7z = Join-Path $env:ProgramFiles '7-Zip\7z.exe'
$pfx86 = if($env:ProgramFiles -ne $env:ProgramFiles){''} else {''}
$pf86env = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)','Process')
$pf86Path = if($pf86env){ Join-Path $pf86env '7-Zip\7z.exe' } else { '' }
$fallback = [ordered]@{
  programfiles_7z_path=$pf7z
  programfiles_7z_exists=(Test-Path -LiteralPath $pf7z)
  programfiles_x86_7z_path=$pf86Path
  programfiles_x86_7z_exists=($pf86Path -and (Test-Path -LiteralPath $pf86Path))
}

$toolStates=[ordered]@{
  winget=($results | Where-Object { $_.id -eq 'winget_version' } | Select-Object -First 1).exit_code -eq 0
  node=($results | Where-Object { $_.id -eq 'node_version' } | Select-Object -First 1).exit_code -eq 0
  npm=($results | Where-Object { $_.id -eq 'npm_version' } | Select-Object -First 1).exit_code -eq 0
  python=($results | Where-Object { $_.id -eq 'python_version' } | Select-Object -First 1).exit_code -eq 0
  pip=($results | Where-Object { $_.id -eq 'python_pip_version' } | Select-Object -First 1).exit_code -eq 0
  tool_7zip_cli=(($results | Where-Object { $_.id -eq 'tool_7z_info' } | Select-Object -First 1).exit_code -eq 0) -or $fallback.programfiles_7z_exists -or $fallback.programfiles_x86_7z_exists
  tool_markdownlint=(($results | Where-Object { $_.id -eq 'tool_markdownlint_version' } | Select-Object -First 1).exit_code -eq 0)
  tool_check_jsonschema=((($results | Where-Object { $_.id -eq 'tool_check_jsonschema_version' } | Select-Object -First 1).exit_code -eq 0) -or (($results | Where-Object { $_.id -eq 'tool_python_module_check_jsonschema_version' } | Select-Object -First 1).exit_code -eq 0))
  tool_yamllint=((($results | Where-Object { $_.id -eq 'tool_yamllint_version' } | Select-Object -First 1).exit_code -eq 0) -or (($results | Where-Object { $_.id -eq 'tool_python_module_yamllint_version' } | Select-Object -First 1).exit_code -eq 0))
}

$payload=[ordered]@{
  task_id='TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1'
  generated_at_utc=(Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  raw_dir=$RawDir
  fallback_checks=$fallback
  checks=$results
  state_summary=$toolStates
}
$invJson = Join-Path $ReportRoot 'preinstall_inventory.json'
$invMd = Join-Path $ReportRoot 'preinstall_inventory.md'
($payload | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $invJson -Encoding utf8

$md = @()
$md += '# Preinstall Inventory'
$md += ''
$md += "- task_id: $($payload.task_id)"
$md += "- generated_at_utc: $($payload.generated_at_utc)"
$md += ''
$md += '## State summary'
foreach($k in $toolStates.Keys){
  $md += "- ${k}: $($toolStates[$k])"
}
$md += ''
$md += '## Fallback 7-Zip paths'
$md += "- ProgramFiles: $($fallback.programfiles_7z_path) (exists=$($fallback.programfiles_7z_exists))"
$md += "- ProgramFiles(x86): $($fallback.programfiles_x86_7z_path) (exists=$($fallback.programfiles_x86_7z_exists))"
$md += ''
$md += '## Command checks'
foreach($r in $results){
  $md += "- [$($r.id)] exit=$($r.exit_code) cmd=`$ $($r.command)"
}
Set-Content -LiteralPath $invMd -Value ($md -join "`n") -Encoding utf8
Write-Output ($payload | ConvertTo-Json -Depth 4)
