param(
    [string]$RepoRoot = "",
    [string]$RegisterZip = "",
    [string]$ResolveTaskId = "",
    [switch]$ResolveCurrent,
    [switch]$ShowCurrent,
    [switch]$PreflightOnly,
    [string]$PreflightReceiptPath = ""
)

$ErrorActionPreference = "Stop"

$launcherPy = Join-Path $PSScriptRoot "..\TOOLS\astronomicon_owner_launcher_v0_1.py"
if (-not (Test-Path $launcherPy)) {
    Write-Error "Launcher script not found: $launcherPy"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
}

$args = @($launcherPy, "--repo-root", $RepoRoot)

if (-not [string]::IsNullOrWhiteSpace($RegisterZip)) {
    $args += @("--register-zip", $RegisterZip)
}
if (-not [string]::IsNullOrWhiteSpace($ResolveTaskId)) {
    $args += @("--resolve-task-id", $ResolveTaskId)
}
if ($ResolveCurrent.IsPresent) {
    $args += "--resolve-current"
}
if ($ShowCurrent.IsPresent) {
    $args += "--show-current"
}
if ($PreflightOnly.IsPresent) {
    $args += "--preflight-only"
}
if (-not [string]::IsNullOrWhiteSpace($PreflightReceiptPath)) {
    $args += @("--preflight-receipt-path", $PreflightReceiptPath)
}

Write-Host "Running Astronomicon owner launcher with mandatory bootstrap preflight..."
& python @args
exit $LASTEXITCODE
