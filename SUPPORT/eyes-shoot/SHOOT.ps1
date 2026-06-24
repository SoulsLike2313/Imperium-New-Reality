# EYES-PLAYWRIGHT-HARNESS-0001 :: SHOOT
# Drives Playwright over V0..V6 of the viewer and dumps PNGs to .\out\
# Usage:
#   .\SHOOT.ps1                                        # local http.server, default views
#   .\SHOOT.ps1 -Views "V0,V1,V2"                      # subset
#   .\SHOOT.ps1 -ViewerUrl "https://.../SUPPORT/viewer/"   # use remote (e.g. GitHub Pages)
#   .\SHOOT.ps1 -Width 2560 -Height 1600 -Scale 2      # higher-res
param(
    [string]$RepoRoot = $null,
    [string]$Views = "V0,V1,V2,V3,V4,V5,V6",
    [string]$ViewerUrl = $null,
    [int]$Width = 1920,
    [int]$Height = 1200,
    [int]$Scale = 2,
    [int]$WaitMs = 60000,
    [int]$SettleMs = 3000,
    [int]$Port = 0
)
$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null

if (-not $RepoRoot) {
    # Two levels up from SUPPORT\eyes-shoot\
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\")).Path
}

$py = "python"
try { & python --version | Out-Null 2>$null } catch { $py = "python3" }

$script = Join-Path $PSScriptRoot "shoot.py"
if (-not (Test-Path $script)) { throw "[SHOOT] shoot.py not found at $script" }

$outDir = Join-Path $PSScriptRoot "out"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }

Write-Host "[SHOOT] repo:    $RepoRoot"
Write-Host "[SHOOT] script:  $script"
Write-Host "[SHOOT] out:     $outDir"
Write-Host "[SHOOT] views:   $Views"
Write-Host "[SHOOT] size:    $($Width)x$($Height) (scale=$Scale)"
Write-Host ""

$pyArgs = @(
    $script,
    "--repo-root", $RepoRoot,
    "--out-dir",   $outDir,
    "--views",     $Views,
    "--width",     $Width,
    "--height",    $Height,
    "--scale",     $Scale,
    "--wait-ms",   $WaitMs,
    "--settle-ms", $SettleMs
)
if ($ViewerUrl) { $pyArgs += @("--viewer-url", $ViewerUrl) }
if ($Port -gt 0) { $pyArgs += @("--port", $Port) }

& $py @pyArgs
if ($LASTEXITCODE -ne 0) { throw "[SHOOT] shoot.py failed (rc=$LASTEXITCODE). Did you run INSTALL.ps1?" }

Write-Host ""
Write-Host "[SHOOT] PASS. PNGs in: $outDir"
Get-ChildItem $outDir -Filter "*.png" | Sort-Object Name | ForEach-Object {
    Write-Host ("  {0,-10} {1,9} bytes" -f $_.Name, $_.Length)
}
