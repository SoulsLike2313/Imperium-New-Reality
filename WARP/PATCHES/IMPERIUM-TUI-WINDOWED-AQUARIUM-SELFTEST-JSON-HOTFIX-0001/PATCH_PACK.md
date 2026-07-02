# PATCH PACK — IMPERIUM-TUI-WINDOWED-AQUARIUM-SELFTEST-JSON-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/TUI`  
mode: `WINDOWED_TUI_VALIDATOR_HOTFIX`

## Purpose

Fix false failure:

```text
selftest did not report enough actions
```

## Diagnosis

The launcher self-test likely emitted valid JSON, but PowerShell profile text such as:

```text
IMPERIUM SHELL: pwsh 7.6.2 OK
```

can appear before the JSON.

The previous validator tried `json.loads(stdout)` on the entire stdout and failed to parse `action_count`.

## Fix

The validator now extracts a balanced JSON object from noisy stdout and falls back to manifest action count only when selftest verdict is PASS.

## Expected verdict

```text
PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_READY
```
