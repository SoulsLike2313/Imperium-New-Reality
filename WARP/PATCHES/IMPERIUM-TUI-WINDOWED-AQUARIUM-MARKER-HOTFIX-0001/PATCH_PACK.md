# PATCH PACK — IMPERIUM-TUI-WINDOWED-AQUARIUM-MARKER-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/TUI`  
mode: `WINDOWED_TUI_VALIDATOR_HOTFIX`

## Purpose

Fix false failure:

```text
windowed launcher missing UI markers
```

## Diagnosis

The launcher existed, but validator was too brittle. It expected literal marker `-SelfTest` in source text, while the actual PowerShell parameter is:

```powershell
[switch]$SelfTest
```

The hotfix validates the real `-SelfTest` execution path and checks UI shape structurally.

## Expected verdict

```text
PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_READY
```
