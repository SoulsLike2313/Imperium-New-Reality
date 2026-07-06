Run from repo root after unpack/apply:

```powershell
pwsh WARP/PATCHES/IMPERIUM-CORE-SELF-ANALYSIS-0001/RUN_IMPERIUM-CORE-SELF-ANALYSIS-0001.ps1
```

Then inspect:

```powershell
$summary = Get-Content "SUPPORT/APP_TAURI/receipts/imperium_core_self_analysis_summary.json" -Raw | ConvertFrom-Json
$summary | Format-List
```
