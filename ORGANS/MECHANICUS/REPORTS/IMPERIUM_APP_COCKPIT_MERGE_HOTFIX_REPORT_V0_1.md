# IMPERIUM APP COCKPIT MERGE HOTFIX REPORT V0.1

task_id: `IMPERIUM-APP-COCKPIT-MERGE-HOTFIX-0001`  
validator_id: `mechanicus_imperium_app_cockpit_merge_hotfix_validator.v0_1`  
verdict: `PASS_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_READY`  
generated_at_utc: `2026-07-04T00:29:36Z`

## Meaning

The previous cockpit patch made Patch Registry and Language Codex feel like a separate replacement app.

This hotfix restores the existing Imperium App Platform shape and embeds operational powers as rooms:

- Organ Hub;
- Patch Forge / Patch Pack Registry;
- Mechanicus / Language Power Codex;
- Aquarium;
- future Eyes/Seed Core rooms.

## Checks

- `PASS` — tauri_main_js_exists
- `PASS` — main_js_contains_existing_app_room_markers_and_cockpit_powers
- `PASS` — main_js_restores_platform_as_primary_app_not_operational_cockpit_title
- `PASS` — patch_registry_is_room_inside_app
- `PASS` — mechanicus_language_codex_is_room_inside_app
- `PASS` — runtime_fps_proof_marker_preserved
- `PASS` — tauri_styles_css_exists
- `PASS` — styles_css_contains_platform_room_layout_markers
- `PASS` — tauri_package_json_exists

## Warnings

- none

## Errors

- none
