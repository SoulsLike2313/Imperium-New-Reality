# KPD Scorecard Report

## Repair

`show-kpd` now starts default output with a compact scorecard:

- overall KPD;
- evidence quality;
- trust risk;
- runtime cost;
- warnings;
- recommended next action.

Full detail remains in JSON and verbose output.

## Evidence

- `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185128-cd11a4/reports/kpd_score.json`

The observed KPD verdict was WARN/BLOCKED for the active check-all run because warnings and dirty admitted state are now visible. This is expected no-fake-green behavior, not a scorecard failure.

