$ErrorActionPreference = "Stop"

$Repo = Get-Location
Write-Host "Installing THRONE-KERNEL-ANATOMY-AND-CORE-V1-TARGET-0001 into: $Repo"

if (-not (Test-Path ".git")) { throw "Run this from repository root." }

$PatchDir = "WARP\PATCHES\THRONE-KERNEL-ANATOMY-AND-CORE-V1-TARGET-0001"
if (-not (Test-Path $PatchDir)) { throw "Patch dir not found after extraction: $PatchDir" }

Write-Host "Patch present: $PatchDir"
Write-Host ""
Write-Host "Run validation:"
Write-Host "pwsh WARP/PATCHES/THRONE-KERNEL-ANATOMY-AND-CORE-V1-TARGET-0001/RUN_THRONE_KERNEL_ANATOMY_VALIDATION.ps1"
Write-Host ""
Write-Host "Run validation + refresh census + target gap:"
Write-Host "pwsh WARP/PATCHES/THRONE-KERNEL-ANATOMY-AND-CORE-V1-TARGET-0001/RUN_AND_REFRESH_THRONE_MAP.ps1"
