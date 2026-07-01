# ASTRONOMICON DRY-RUN AND LAUNCHER VALIDATION REPORT

task_id: `IMPERIUM-LAUNCHER-ASTRONOMICON-DRY-RUN-0001`  
validator_id: `astronomicon_dry_run_and_launcher_validator.v0_1`  
verdict: `PASS_LAUNCHER_AND_ASTRONOMICON_DRY_RUN_READY`

## Samples
- `SELFTEST-WITCHER3-60FPS-0001` expected `EXTERNAL_GAME_OPTIMIZATION`, got `EXTERNAL_GAME_OPTIMIZATION`, execution_allowed `False`, missing `18`
- `SELFTEST-GAME-BUILD-0001` expected `SOFTWARE_PRODUCT_BUILD`, got `SOFTWARE_PRODUCT_BUILD`, execution_allowed `False`, missing `18`
- `SELFTEST-IMPERIUM-PATCH-0001` expected `IMPERIUM_PATCH_PACK`, got `IMPERIUM_PATCH_PACK`, execution_allowed `False`, missing `17`

## Checks
- `PASS` — imperium.ps1_exists
- `PASS` — imperium_cli.py_exists
- `PASS` — LAUNCHER_COMMANDS_V0_1.json_exists
- `PASS` — astronomicon_intake_dry_run.py_exists
- `PASS` — TASK_SHAPE_FAMILY_MATRIX_V0_1.json_exists
- `PASS` — UNIVERSAL_TASK_INFORMATION_DEFICIT_MATRIX_V0_1.json_exists
- `PASS` — task_intake_packet.schema.json_exists
- `PASS` — focus_pack.schema.json_exists
- `PASS` — LAUNCHER_COMMANDS_V0_1.json_parses
- `PASS` — TASK_SHAPE_FAMILY_MATRIX_V0_1.json_parses
- `PASS` — UNIVERSAL_TASK_INFORMATION_DEFICIT_MATRIX_V0_1.json_parses
- `PASS` — SELFTEST-WITCHER3-60FPS-0001_dry_run_executes
- `PASS` — SELFTEST-WITCHER3-60FPS-0001_required_artifacts_exist
- `PASS` — SELFTEST-WITCHER3-60FPS-0001_classification_EXTERNAL_GAME_OPTIMIZATION
- `PASS` — SELFTEST-WITCHER3-60FPS-0001_execution_blocked
- `PASS` — SELFTEST-WITCHER3-60FPS-0001_missing_context_detected
- `PASS` — SELFTEST-GAME-BUILD-0001_dry_run_executes
- `PASS` — SELFTEST-GAME-BUILD-0001_required_artifacts_exist
- `PASS` — SELFTEST-GAME-BUILD-0001_classification_SOFTWARE_PRODUCT_BUILD
- `PASS` — SELFTEST-GAME-BUILD-0001_execution_blocked
- `PASS` — SELFTEST-GAME-BUILD-0001_missing_context_detected
- `PASS` — SELFTEST-IMPERIUM-PATCH-0001_dry_run_executes
- `PASS` — SELFTEST-IMPERIUM-PATCH-0001_required_artifacts_exist
- `PASS` — SELFTEST-IMPERIUM-PATCH-0001_classification_IMPERIUM_PATCH_PACK
- `PASS` — SELFTEST-IMPERIUM-PATCH-0001_execution_blocked
- `PASS` — SELFTEST-IMPERIUM-PATCH-0001_missing_context_detected
- `PASS` — launcher_is_non_mutating_this_patch
- `PASS` — astronomicon_dry_run_does_not_claim_trust_or_execution

## Errors
- none
