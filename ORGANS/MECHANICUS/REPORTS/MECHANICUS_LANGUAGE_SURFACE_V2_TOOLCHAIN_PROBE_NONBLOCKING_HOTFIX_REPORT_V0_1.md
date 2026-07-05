# MECHANICUS LANGUAGE SURFACE V2 TOOLCHAIN PROBE NONBLOCKING HOTFIX REPORT V0.1

task_id: `MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-PROBE-NONBLOCKING-HOTFIX-0001`  
validator_id: `mechanicus_language_surface_v2_toolchain_probe_nonblocking_hotfix_validator.v0_1`  
verdict: `FAIL_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_NONBLOCKING_HOTFIX`  
generated_at_utc: `2026-07-04T18:48:36Z`

## Diagnosis

The previous patch failed because the first toolchain probe treated host/tool availability as a hard blocker too early:

```text
toolchain probe failed required tools
```

For the first Mechanicus baseline this is too strict. A missing or subprocess-invisible tool must become capability debt, not a false PASS and not a patch stopper.

## Fix

- installs `mechanicus_toolchain_probe.v0_2_nonblocking_baseline`;
- writes toolchain proof report even when some tools fail;
- keeps `not_claimed` boundary;
- reruns the previous validator and requires its receipt to become PASS.

## Checks

- `PASS` — nonblocking_toolchain_probe_installed
- `FAIL` — nonblocking_toolchain_probe_runs_and_returns_zero
- `PASS` — previous_language_surface_v2_validator_exists
- `FAIL` — previous_language_surface_v2_receipt_is_pass_after_hotfix

## Warnings

- none

## Errors

- nonblocking toolchain probe did not run/write report
