param(
  [string]$CommandsFile = "",
  [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"

$LauncherPath = $MyInvocation.MyCommand.Path
$LauncherDir = Split-Path -Parent $LauncherPath
$RepoRoot = Resolve-Path (Join-Path $LauncherDir "..\\..\\..\\..")
$RunnerPath = Join-Path $RepoRoot "IMPERIUM_NEW_GENERATION\\ORGAN_AGENTS\\OFFICIO_AGENTIS_AGENT\\TOOLS\\officio_agent_runner.py"
$RuntimeRoot = "E:\\IMPERIUM_CONTEXT\\LOCAL\\OFFICIO_AGENTIS\\RUNS"
$env:OFFICIO_RUNTIME_ROOT = $RuntimeRoot
$CallerCwd = (Get-Location).Path

$ResolvedCommandsFile = ""
if ($CommandsFile -ne "") {
  if ([System.IO.Path]::IsPathRooted($CommandsFile)) {
    $ResolvedCommandsFile = $CommandsFile
  } else {
    $ResolvedCommandsFile = Join-Path $CallerCwd $CommandsFile
  }
  if (-not (Test-Path -LiteralPath $ResolvedCommandsFile)) {
    Write-Error "[OFFICIO] commands file missing: $ResolvedCommandsFile"
    exit 1
  }
}

Write-Host "[OFFICIO] launcher_path=$LauncherPath"
Write-Host "[OFFICIO] caller_cwd=$CallerCwd"
Write-Host "[OFFICIO] repo_root=$RepoRoot"
Write-Host "[OFFICIO] runner_path=$RunnerPath"
Write-Host "[OFFICIO] runtime_root=$RuntimeRoot"

if (-not (Test-Path $RunnerPath)) {
  Write-Error "[OFFICIO] runner missing: $RunnerPath"
  exit 1
}

$PythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
  $PythonCmd = @("py", "-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $PythonCmd = @("python")
} else {
  Write-Error "[OFFICIO] Python is not available (py/python not found)."
  exit 1
}

Write-Host "[OFFICIO] python_cmd=$($PythonCmd -join ' ')"
Write-Host "[OFFICIO] renderer_hint=runner will write renderer_diagnostic.json"

Push-Location $RepoRoot
try {
  $cmd = @($PythonCmd + @($RunnerPath, "shell"))
  if ($ResolvedCommandsFile -ne "") {
    $cmd += @("--commands-file", $ResolvedCommandsFile)
  }
  if ($NonInteractive) {
    $cmd += "--non-interactive"
  }

  Write-Host "[OFFICIO] exec=$($cmd -join ' ')"
  & $cmd[0] $cmd[1..($cmd.Length - 1)]
  exit $LASTEXITCODE
}
finally {
  Pop-Location
}
