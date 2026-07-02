# PATCH PACK — IMPERIUM-APP-TAURI-RUNTIME-WINDOW-FPS-PROOF-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/APP_TAURI`  
mode: `RUNTIME_WINDOW_FPS_PROOF`

## Purpose

Open the Tauri app locally and prove a WebView runtime FPS lock with a receipt.

## What it changes

```text
SUPPORT/APP_TAURI/src/main.js
SUPPORT/APP_TAURI/src-tauri/src/main.rs
SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_WINDOW_FPS_PROOF_CONTRACT_V0_1.json
ORGANS/ASTRONOMICON/VALIDATORS/validate_imperium_app_tauri_runtime_window_fps_proof.py
```

## Proof

The validator runs:

```powershell
cd SUPPORT/APP_TAURI
cmd.exe /d /s /c "npm run tauri:dev"
```

The opened WebView measures `requestAnimationFrame`, calls Rust command:

```text
record_runtime_fps_proof
```

and writes:

```text
SUPPORT/APP_TAURI/receipts/*_runtime_fps_proof_receipt.json
```

## Strict FPS gate

```text
target_fps: 60
average_fps_pass_threshold: 59.5
minimum_sample_count: 180
max_slow_frame_ratio: 0.05
```

## Expected verdict

```text
PASS_IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_READY
```

## Not claimed

```text
packaged exe built
auto-updater active
Eyes embedded
AAA final polish complete
```
