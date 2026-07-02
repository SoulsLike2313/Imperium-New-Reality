# PATCH PACK — IMPERIUM-APP-TAURI-PROOF-RUN-ICON-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/APP_TAURI`  
mode: `TAURI_ICON_RESOURCE_HOTFIX`

## Purpose

Close the Tauri proof-run cargo failure:

```text
`icons/icon.ico` not found; required for generating a Windows Resource file during tauri-build
```

## Fix

Adds:

```text
SUPPORT/APP_TAURI/src-tauri/icons/icon.ico
SUPPORT/APP_TAURI/src-tauri/icons/icon.png
```

and updates:

```text
SUPPORT/APP_TAURI/src-tauri/tauri.conf.json
```

to reference:

```text
icons/icon.ico
icons/icon.png
```

## Expected verdict

```text
PASS_IMPERIUM_APP_TAURI_PROOF_RUN_ICON_HOTFIX_READY
```

and the proof-run receipt should become:

```text
PASS_IMPERIUM_APP_TAURI_PROOF_RUN_READY
```
