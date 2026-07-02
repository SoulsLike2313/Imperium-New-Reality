# PATCH PACK — IMPERIUM-APP-TAURI-SHELL-FRONTEND-MARKER-HOTFIX-FIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/APP_TAURI`  
mode: `ROBUST_IN_PLACE_HOTFIX`

## Purpose

Close the failed previous hotfix.

The previous hotfix still reported:

```text
frontend shell marker still missing from main.js
foundation validator still does not pass after marker hotfix
```

## Fix

This patch does not rely on copying a replacement `main.js`.

It patches the live file in-place:

```text
SUPPORT/APP_TAURI/src/main.js
```

and inserts:

```text
const IMPERIUM_TAURI_SHELL = "IMPERIUM_TAURI_SHELL";
```

after ES import lines, so module syntax remains valid.

Then it reruns the original Tauri foundation validator.

## Expected verdict

```text
PASS_IMPERIUM_APP_TAURI_SHELL_FRONTEND_MARKER_HOTFIX_FIX_READY
```

and the foundation receipt should become:

```text
PASS_IMPERIUM_APP_TAURI_SHELL_FOUNDATION_READY
```
