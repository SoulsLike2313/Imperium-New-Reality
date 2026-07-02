# IMPERIUM APP TAURI PROOF RUN REPORT V0.2

task_id: `IMPERIUM-APP-TAURI-PROOF-RUN-0001`  
validator_id: `imperium_app_tauri_proof_run_validator.v0_2_windows_cmd_aware`  
verdict: `PASS_IMPERIUM_APP_TAURI_PROOF_RUN_READY`  
generated_at_utc: `2026-07-02T14:40:42Z`

## Meaning

This proof-run is Windows-aware: npm commands are executed through `cmd.exe /d /s /c` so `npm.cmd` is resolved the same way as in an operator terminal.

It verifies environment, installs npm dependencies, checks FPS/action contracts, builds the frontend, and compiles/checks the Rust bridge.

It still does not claim the interactive Tauri window or WebView FPS measurement; that is the next runtime proof patch.

## Commands

- `PASS` — `node --version` actual=`node --version` exit=`0`
- `PASS` — `npm --version` actual=`cmd.exe /d /s /c npm --version` exit=`0`
- `PASS` — `cargo --version` actual=`cargo --version` exit=`0`
- `PASS` — `rustc --version` actual=`rustc --version` exit=`0`
- `PASS` — `npm install` actual=`cmd.exe /d /s /c npm install` exit=`0`
- `PASS` — `npm run check:fps` actual=`cmd.exe /d /s /c npm run check:fps` exit=`0`
- `PASS` — `npm run check:parity` actual=`cmd.exe /d /s /c npm run check:parity` exit=`0`
- `PASS` — `npm run build` actual=`cmd.exe /d /s /c npm run build` exit=`0`
- `PASS` — `cargo check --manifest-path SUPPORT/APP_TAURI/src-tauri/Cargo.toml` actual=`cargo check --manifest-path SUPPORT/APP_TAURI/src-tauri/Cargo.toml` exit=`0`

## Checks

- `PASS` — proof_run_matrix_parses
- `PASS` — foundation_receipt_is_pass
- `PASS` — required_tauri_proof_files_exist
- `PASS` — env_node_exists
- `PASS` — env_npm_exists
- `PASS` — env_cargo_exists
- `PASS` — env_rustc_exists
- `PASS` — vite_and_tauri_dev_ports_match_1420
- `PASS` — tauri_generated_artifacts_ignored
- `PASS` — command_node_version_passes
- `PASS` — command_npm_version_passes
- `PASS` — command_cargo_version_passes
- `PASS` — command_rustc_version_passes
- `PASS` — npm_install_passes
- `PASS` — npm_check_fps_passes
- `PASS` — npm_check_parity_passes
- `PASS` — npm_frontend_build_passes
- `PASS` — cargo_check_tauri_bridge_passes
- `PASS` — generated_dirs_can_exist_but_are_ignored

## Warnings

- none

## Errors

- none
