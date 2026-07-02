# PATCH PACK — IMPERIUM-APP-TAURI-SHELL-FRONTEND-MARKER-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/APP_TAURI`  
mode: `FOUNDATION_VALIDATOR_HOTFIX`

## Purpose

Fix the failed Tauri foundation validation:

```text
frontend missing markers
```

Root cause:

```text
IMPERIUM_TAURI_SHELL marker existed in index.html,
but the validator checks only src/main.js + src/styles.css.
```

## Fix

Adds the marker to:

```text
SUPPORT/APP_TAURI/src/main.js
```

and reruns the original foundation validator.

## Expected verdict

```text
PASS_IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_READY
```

The original foundation validator should also emit:

```text
PASS_IMPERIUM_APP_TAURI_SHELL_FOUNDATION_READY
```
