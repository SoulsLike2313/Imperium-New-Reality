# PATCH PACK — IMPERIUM-APP-TAURI-PROOF-RUN-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/APP_TAURI`  
mode: `TAURI_INSTALL_BUILD_COMPILE_PROOF`

## Purpose

Prove the migration foundation can actually install/build/check.

This patch adds:

```text
SUPPORT/APP_TAURI/vite.config.js
SUPPORT/APP_TAURI/.gitignore
fixed SUPPORT/APP_TAURI/src-tauri/src/main.rs
proof-run validator
```

## Expected verdict

```text
PASS_IMPERIUM_APP_TAURI_PROOF_RUN_READY
```

## What it proves

```text
node/npm/cargo/rustc visible
npm install passes
FPS contract check passes
action parity contract passes
frontend build passes
Rust bridge cargo check passes
```

## Not claimed

```text
interactive Tauri window opened
runtime WebView FPS measured
packaged exe built
auto-updater active
Eyes embedded
AAA final polish
```

## Next stage

```text
IMPERIUM-APP-TAURI-RUNTIME-WINDOW-FPS-PROOF-0001
```
