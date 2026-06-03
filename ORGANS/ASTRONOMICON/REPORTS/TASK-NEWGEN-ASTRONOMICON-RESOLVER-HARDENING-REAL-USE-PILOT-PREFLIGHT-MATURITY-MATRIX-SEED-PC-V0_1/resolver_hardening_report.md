# Resolver Hardening Report

Task ID: `TASK-NEWGEN-ASTRONOMICON-RESOLVER-HARDENING-REAL-USE-PILOT-PREFLIGHT-MATURITY-MATRIX-SEED-PC-V0_1`
Timestamp UTC: `2026-05-30T23:59:08Z`

## Hardened files

- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_entry_lib_v0_1.py`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ID_RESOLVER_CONTRACT.json`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_ADMISSION_CONTRACT.json`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_INTAKE_CONTRACT.json`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ENTRY_CORRIDOR_CONTRACT.json`
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/run_stage2_1_resolver_hardening_fixtures_v0_1.py`

## Implemented hardening coverage

1. Missing `task_id` admission block.
2. Duplicate `task_id` detection across stage2 + stage1 registry data.
3. Registered artifact missing detection.
4. `current_expected_task` pointing to missing task detection.
5. Missing route manifest detection.
6. Route manifest missing required 8 organs detection.
7. Malformed admission receipt detection.
8. Unsafe registered path/path traversal detection.
9. Extracted manifest `task_id` mismatch detection.
10. `start task` request without `task_id` and without current expected task detection.
11. Root `_TASKPACK_INBOX` canonical misuse detection.
12. Corrupt registry JSON detection.

## Positive resolver proof

- Admission verdict for this real taskpack: `ADMISSION_PASS`
- Resolve by explicit task_id verdict: `PASS_WITH_WARNINGS`
- Resolve by current expected verdict: `PASS_WITH_WARNINGS`
- Resolver returns required paths (`taskpack_zip_path`, `extracted_path`, `route_manifest_path`, `admission_receipt_path`): `yes`

## Residual warnings

- Stage inherited caps remain active (`CAP_STAGE1_WITH_WARNINGS_ONLY`, `CAP_NO_IDE_VISUAL_RELEASE_YET`, `CAP_NO_WARP_RUNTIME`).
- Clean PASS is not claimed in this stage.
