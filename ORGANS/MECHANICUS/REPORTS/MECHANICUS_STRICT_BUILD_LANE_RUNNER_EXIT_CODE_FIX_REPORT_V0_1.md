# MECHANICUS STRICT BUILD LANE RUNNER EXIT CODE FIX REPORT V0.1

task_id: `MECHANICUS-STRICT-BUILD-LANE-RUNNER-EXIT-CODE-FIX-0001`  
validator_id: `mechanicus_strict_build_lane_runner_exit_code_fix_validator.v0_1`  
verdict: `FAIL_MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_FIX`  
generated_at_utc: `2026-07-05T20:31:21Z`

## Fix

The build runner now follows its report:

```text
PASS report + blocking_failure_count 0 => process exit 0
FAIL report or blocking failures      => process exit 1
```

It also prints a compact ASCII-safe summary instead of dumping the full report to stdout.

## Checks

- `PASS` — runner_exit_code_patcher_installed
- `FAIL` — runner_exit_code_patch_applies_cleanly
- `FAIL` — runner_contains_v0_2_exit_code_and_legacy_validator_markers

## Warnings

- none

## Errors

- runner exit-code patch did not apply cleanly
- runner markers incomplete after patch
