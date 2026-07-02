# IMPERIUM APP TAURI RUNTIME WINDOW FPS PROOF REPORT V0.1

task_id: `IMPERIUM-APP-TAURI-RUNTIME-WINDOW-FPS-PROOF-0001`  
validator_id: `imperium_app_tauri_runtime_window_fps_proof_validator.v0_1`  
verdict: `PASS_IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_READY`  
generated_at_utc: `2026-07-02T14:50:50Z`

## Meaning

This is the first local runtime proof for the Tauri application.

It opens the Tauri dev window, lets the WebView measure `requestAnimationFrame` frame cadence, writes an app-side FPS receipt through the Rust bridge, then closes the process tree.

## Commands

- `PASS` — `npm run tauri:dev` exit=`1`

## Runtime receipt

```text
SUPPORT/APP_TAURI/receipts/20260702_145049_runtime_fps_proof_receipt.json
```

## Checks

- `PASS` — runtime_fps_matrix_parses
- `PASS` — tauri_install_build_compile_proof_is_pass
- `PASS` — runtime_required_files_exist
- `PASS` — frontend_runtime_fps_markers_present
- `PASS` — rust_runtime_fps_command_markers_present
- `PASS` — tauri_dev_window_created_runtime_fps_receipt
- `PASS` — runtime_fps_lock_receipt_is_pass
- `PASS` — runtime_fps_metrics_meet_strict_gate

## Warnings

- none

## Errors

- none
