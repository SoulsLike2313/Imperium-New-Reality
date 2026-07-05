# TESTS — MECHANICUS-ORGAN-READINESS-ROLLUP-0001

Owner-host protocol follows the established Imperium WARP pattern: download zip, find it from repo root / Downloads / Desktop, expand to repo root, then run the patch runner under `WARP/PATCHES/<PATCH_ID>/`.

```powershell
cd E:\IMPERIUM_REALITY

$Zip = Get-ChildItem -Path @(
  ".",
  "$env:USERPROFILE\Downloads",
  "$env:USERPROFILE\Desktop"
) -Filter "mechanicus_organ_readiness_rollup_0001*.zip" -File -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $Zip) {
  throw "Zip не найден. Скачай mechanicus_organ_readiness_rollup_0001.zip и положи его в E:\IMPERIUM_REALITY или Downloads."
}

Expand-Archive -LiteralPath $Zip.FullName -DestinationPath . -Force

pwsh WARP/PATCHES/MECHANICUS-ORGAN-READINESS-ROLLUP-0001/RUN_MECHANICUS_ORGAN_READINESS_ROLLUP.ps1
```

Expected shell line: `IMPERIUM SHELL: pwsh 7.6.2 OK`.

Expected verdict: `PASS_MECHANICUS_ORGAN_READINESS_ROLLUP_READY`.

Expected meaning: rollup exists and preserves `MEASURED_NOT_ASSEMBLED` truth. This does not assemble Mechanicus.

Direct Python execution is only an inner validator check after files have landed, not the Owner-facing patch installation protocol.
