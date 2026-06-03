# Owner Launcher Report

Task: `TASK-NEWGEN-STAGE3-ASTRONOMICON-BOOTSTRAP-HARDENING-UTF8-PREFLIGHT-PC-V0_1`

## Added launcher artifacts

- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_owner_launcher_v0_1.py`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/LAUNCHERS/launch_astronomicon_task_entry_v0_1.ps1`

## Owner-facing behavior

- Always runs bootstrap preflight before intake/resolve/TUI.
- On preflight BLOCK, launcher stops and prints repair command:
  `python IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_bootstrap_repair_v0_1.py --repo-root <repo> --force`
- Does not auto-discover or auto-select fixture runners as launcher target.

## Executed checks

1. `powershell -ExecutionPolicy Bypass -File IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/LAUNCHERS/launch_astronomicon_task_entry_v0_1.ps1 -RepoRoot . -PreflightOnly` -> `PASS`.
2. `python IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_owner_launcher_v0_1.py --repo-root . --show-current` -> `PASS`, current expected task printed.
