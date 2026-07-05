# TESTS - MECHANICUS-TOOL-ADMISSION-V2-0001

Primary test is the WARP runner:

```powershell
pwsh WARP/PATCHES/MECHANICUS-TOOL-ADMISSION-V2-0001/RUN_MECHANICUS_TOOL_ADMISSION_V2.ps1
```

It copies FILES_TO_LAND, runs the validator with `--apply`, writes reports/receipt, and fails on blocking errors.
