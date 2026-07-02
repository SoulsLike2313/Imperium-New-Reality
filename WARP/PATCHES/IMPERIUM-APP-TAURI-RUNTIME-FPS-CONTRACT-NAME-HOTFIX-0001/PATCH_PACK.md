# PATCH PACK — IMPERIUM-APP-TAURI-RUNTIME-FPS-CONTRACT-NAME-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/APP_TAURI`  
mode: `CONTRACT_FILENAME_HOTFIX`

## Purpose

Close the runtime FPS proof failure:

```text
runtime proof required files missing
```

## Diagnosis

The runtime FPS matrix expects this exact file:

```text
SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_WINDOW_FPS_PROOF_CONTRACT_V0_1.json
```

The previous patch accidentally wrote:

```text
SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_FPS_PROOF_CONTRACT_V0_1.json
```

missing `WINDOW`.

## Fix

Add the canonical expected contract filename and rerun the runtime window FPS proof validator.

## Expected verdict

```text
PASS_IMPERIUM_APP_TAURI_RUNTIME_FPS_CONTRACT_NAME_HOTFIX_READY
```

and the runtime proof receipt should become:

```text
PASS_IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_READY
```
