# PATCH PACK — MECHANICUS-COCKPIT-PATCH-REGISTRY-AND-LANGUAGE-CODEX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + SUPPORT/APP_TAURI`  
mode: `COCKPIT_OPERATIONAL_FORCE_AND_LANGUAGE_CODEX`

## Purpose

Give the Tauri cockpit real operational force:

- discover WARP patch packs;
- register patch packs into app state;
- run registered patch pack runners from the app;
- write app-side patch run receipts/logs;
- expose a Mechanicus language power codex.

## Safety

The cockpit runner is intentionally bounded:

- patch id must be safe;
- patch must exist under `WARP/PATCHES`;
- patch must be registered before run;
- runner must be `RUN_*.ps1`;
- obvious git commit/push and destructive root patterns are blocked;
- app writes logs/receipts for cockpit runs.

This is not a replacement for Owner review, WARP discipline or Throne/Custodes validation.

## Language law

Python binds and orchestrates. Rust judges and guards. Go ships simple fast CLIs. C++ descends only for profiled native hot paths. TypeScript owns app surfaces. PowerShell owns Windows operator runners.

## Not claimed

- Full Mechanicus assembled.
- Full language toolchain scan complete.
- All compilers installed.
- External repo automation ready.
- Safe destructive repair ready.
- Core v1 ready.

## Expected verdict

```text
PASS_MECHANICUS_COCKPIT_PATCH_REGISTRY_AND_LANGUAGE_CODEX_READY
```
