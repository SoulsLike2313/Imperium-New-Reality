# Dirty Admission Report

## Repair

Heavy commands now run a dirty-state admission check:

- `check-all`;
- `build-dossier`;
- `collect-continuity-pack`;
- `collect-reality-snapshot`;
- `build-agent-handoff-context`.

Unauthorized dirty paths return `OWNER_DECISION_REQUIRED` with options. Dirty paths limited to admitted Administratum/RUNS scope continue with WARN, not clean PASS.

## Evidence

Dirty simulation used `ADMINISTRATUM_DIRTY_SIMULATION_PATHS=UNAUTHORIZED_DIRTY_SIMULATION.tmp`.

Evidence path:

- `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-184641-4efb67/reports/collect_reality_snapshot_dirty_admission_report.json`

Result: `OWNER_DECISION_REQUIRED`.

## Verdict

PASS for dirty-state admission law. Current task dirty state is admitted by GATE_ACK scope and remains WARN until commit/cleanup.

