param(
  [ValidateSet('stable', 'candidate', 'legacy')]
  [string]$Mode = 'stable',
  [int]$Port = 8765,
  [string]$RepoRoot = 'E:\IMPERIUM',
  [switch]$NoBrowser
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $RepoRoot)) {
  throw "Repo root not found: $RepoRoot"
}

$relativePath = switch ($Mode) {
  'stable'    { 'IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html' }
  'candidate' { 'IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_candidate.html' }
  'legacy'    { 'IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html' }
}

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
$usePyLauncher = $false
if (-not $pythonCmd) {
  $pyCmd = Get-Command py -ErrorAction SilentlyContinue
  if (-not $pyCmd) {
    throw 'Neither python nor py launcher was found in PATH.'
  }
  $pythonExe = $pyCmd.Source
  $usePyLauncher = $true
} else {
  $pythonExe = $pythonCmd.Source
}

$tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
if (-not $tcp.TcpTestSucceeded) {
  $args = if ($usePyLauncher) {
    @('-3', '-m', 'http.server', "$Port", '--bind', '127.0.0.1')
  } else {
    @('-m', 'http.server', "$Port", '--bind', '127.0.0.1')
  }
  Start-Process -FilePath $pythonExe -ArgumentList $args -WorkingDirectory $RepoRoot -WindowStyle Hidden | Out-Null
  Start-Sleep -Milliseconds 600
}

$url = "http://127.0.0.1:$Port/$relativePath"
if (-not $NoBrowser) {
  Start-Process $url | Out-Null
}

Write-Output "launch_mode=$Mode"
Write-Output "launch_url=$url"
Write-Output "repo_root=$RepoRoot"
