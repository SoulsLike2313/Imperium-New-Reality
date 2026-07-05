# PATCH PACK — MECHANICUS-STRICT-BUILD-LANE-FOUNDATION-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + CUSTODES + THRONE`  
mode: `STRICT_BUILD_LANE_FOUNDATION`

## Purpose

Resolve planner gap:

```text
STRICT_BUILD_LANE_REQUIRED => NEXT_VALIDATOR_REQUIRED
```

This patch gives Mechanicus a build proof lane separate from code cleanliness and runtime truth.

## Lanes

- Python compile current non-patch files;
- PowerShell host probe;
- Tauri frontend `npm run build` when `SUPPORT/APP_TAURI/package.json` exists;
- Tauri Rust `cargo check` when `SUPPORT/APP_TAURI/src-tauri/Cargo.toml` exists.

## Boundary

```text
Build proof is not code cleanliness.
Build proof is not runtime proof.
No dependency installation is attempted.
```
