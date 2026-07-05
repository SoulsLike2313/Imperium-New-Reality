# MECHANICUS LANGUAGE SURFACE V2 TOOLCHAIN PROBE ULTRASAFE HOTFIX REPORT V0.2

task_id: `MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-PROBE-ULTRASAFE-HOTFIX-0002`  
validator_id: `mechanicus_language_surface_v2_toolchain_probe_ultrasafe_hotfix_validator.v0_2`  
verdict: `PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_PROBE_ULTRASAFE_HOTFIX_READY`  
generated_at_utc: `2026-07-04T19:00:49Z`

## Meaning

This hotfix installs an ultrasafe nonblocking toolchain probe. Missing/failing tools are capability debt, not fake pass and not early foundation blocker.

## Checks

- `PASS` — ultrasafe_toolchain_probe_installed
- `PASS` — ultrasafe_probe_runs_and_writes_report
- `PASS` — ultrasafe_probe_report_has_debt_boundary
- `PASS` — previous_language_surface_v2_validator_exists
- `PASS` — previous_language_surface_v2_validator_passes_after_ultrasafe_hotfix
- `PASS` — previous_language_surface_v2_receipt_is_pass_after_ultrasafe_hotfix

## Warnings

- Optional toolchains missing or failed and are recorded as capability debt.
- Build targets were detected but not run by ultrasafe probe; strict build lanes remain separate.
- Optional toolchains/builds missing or failed; recorded as debt, not 100% clean failure.
- Validation baseline contains debt; expected for first baseline.

## Errors

- none
