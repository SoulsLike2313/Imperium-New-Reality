# Mechanicus Code Topology V0.1

- verdict: `PASS_MECHANICUS_CODE_TOPOLOGY_READY`
- generated_at_utc: `2026-07-06T02:09:47Z`
- scope: `SUPPORT/APP_TAURI`
- file_count: `86`
- total_lines: `13683`
- monolith_risk_count: `3`
- blocking_monolith_count: `1`

## Languages

- `JSON`: files=64 lines=8690
- `CSS`: files=1 lines=1913
- `Python`: files=10 lines=1483
- `JavaScript`: files=2 lines=795
- `Rust`: files=2 lines=729
- `Markdown`: files=3 lines=43
- `TOML`: files=1 lines=15
- `PowerShell`: files=2 lines=14
- `HTML`: files=1 lines=1

## Top files by lines

- `SUPPORT/APP_TAURI/src-tauri/gen/schemas/desktop-schema.json` lines=2525 risk=OK zone=APP_FRONTEND_SOURCE
- `SUPPORT/APP_TAURI/src-tauri/gen/schemas/windows-schema.json` lines=2525 risk=OK zone=APP_FRONTEND_SOURCE
- `SUPPORT/APP_TAURI/src/styles.css` lines=1913 risk=BLOCKING_MONOLITH zone=APP_STYLE_SURFACE_MONOLITH_CANDIDATE
- `SUPPORT/APP_TAURI/package-lock.json` lines=1287 risk=OK zone=APP_OTHER
- `SUPPORT/APP_TAURI/src/main.js` lines=780 risk=MONOLITH_RISK zone=APP_FRONTEND_MONOLITH_CANDIDATE
- `SUPPORT/APP_TAURI/src-tauri/src/main.rs` lines=728 risk=MONOLITH_RISK zone=TAURI_RUST_COMMAND_BRIDGE
- `SUPPORT/APP_TAURI/state/patch_pack_registry.json` lines=322 risk=OK zone=APP_OTHER
- `SUPPORT/APP_TAURI/tools/register_patch_with_organs_cli.py` lines=275 risk=OK zone=APP_TERMINAL_TOOLS
- `SUPPORT/APP_TAURI/receipts/astronomicon_mechanicus_registration_proof_receipt.json` lines=231 risk=OK zone=APP_EVIDENCE_RECEIPTS
- `SUPPORT/APP_TAURI/tests/validate_astronomicon_mechanicus_registration.py` lines=222 risk=OK zone=APP_TESTS_VALIDATORS
- `SUPPORT/APP_TAURI/receipts/two_phase_organ_registration_receipt.json` lines=186 risk=OK zone=APP_EVIDENCE_RECEIPTS
- `SUPPORT/APP_TAURI/tools/imperium_core_self_analyze.py` lines=169 risk=OK zone=APP_TERMINAL_TOOLS

## Monolith risks

- `SUPPORT/APP_TAURI/src/styles.css` lines=1913 risk=BLOCKING_MONOLITH
- `SUPPORT/APP_TAURI/src/main.js` lines=780 risk=MONOLITH_RISK
- `SUPPORT/APP_TAURI/src-tauri/src/main.rs` lines=728 risk=MONOLITH_RISK

## Refactor priority

- split SUPPORT/APP_TAURI/src/main.js into shell/nav/astronomicon/mechanicus/proof modules
- split SUPPORT/APP_TAURI/src/styles.css into tokens/layout/components/rooms/proof css
- keep app registration/launch buttons present but terminal remains preferred until UI matures
- build a one-screen proof digest before adding Eyes/Canvas runtime

## Warnings

- monolith risk files visible: 3
- blocking monolith files visible: 1
