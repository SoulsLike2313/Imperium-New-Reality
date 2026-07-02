# PATCH PACK — IMPERIUM-TUI-AQUARIUM-VALIDATOR-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/TUI`  
mode: `TUI_VALIDATOR_HOTFIX`

## Purpose

Fix the first TUI validation failure.

## Failure observed

```text
TUI contains forbidden git operations outside explicit rejection
TUI status action failed or did not show aquarium log
```

## Diagnosis

The validator was too literal:

```text
raw text "git commit" in rejection code != implemented git commit
```

The TUI also now emits a stable ASCII marker:

```text
AQUARIUM_LOG: SUPPORT/TUI/LOGS/...
```

## Expected verdict

```text
PASS_IMPERIUM_TUI_ASTRONOMICON_CONSOLE_READY
```
