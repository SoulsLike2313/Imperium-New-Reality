# Warning Reconciliation Report

## Repair

`_finalize_command` now performs one final warning reconciliation step:

- explicit command warnings are deduplicated;
- internal `metrics.warnings_count` is compared to explicit warnings;
- if internal warnings exceed explicit warnings, a reconciliation warning is added;
- any non-empty warning list upgrades `PASS` to `PASS_WITH_WARNINGS`;
- final rendered status becomes `WARN`, never `PASS/WARNINGS: NONE`.

## Evidence

`check-all` run `RUN-ADMINISTRATUM-20260518-184654-4f05cf` shows:

- `check_all_report.json`: PASS 43/43 tests;
- command verdict: `PASS_WITH_WARNINGS`;
- rendered status: `WARN`;
- warnings include admitted dirty pre-state and internal warning reconciliation.

## Verdict

PASS for R-001 warning accounting behavior. No active warning source is hidden under final PASS.

