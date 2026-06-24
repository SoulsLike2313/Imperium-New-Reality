# EYES-PLAYWRIGHT-HARNESS-0001 :: INSTALL
# One-time installer for Playwright + Chromium (~150MB browser binary).
# Re-running is safe (idempotent on pip + playwright install).
$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null

$py = "python"
try { & python --version | Out-Null 2>$null } catch { $py = "python3" }
Write-Host "[INSTALL] using interpreter: $py"

Write-Host "[INSTALL] step 1/2: pip install playwright"
& $py -m pip install --upgrade playwright
if ($LASTEXITCODE -ne 0) { throw "[INSTALL] pip install playwright failed (rc=$LASTEXITCODE)" }

Write-Host "[INSTALL] step 2/2: playwright install chromium"
& $py -m playwright install chromium
if ($LASTEXITCODE -ne 0) { throw "[INSTALL] playwright install chromium failed (rc=$LASTEXITCODE)" }

Write-Host ""
Write-Host "[INSTALL] PASS. Next: run .\SHOOT.ps1"
