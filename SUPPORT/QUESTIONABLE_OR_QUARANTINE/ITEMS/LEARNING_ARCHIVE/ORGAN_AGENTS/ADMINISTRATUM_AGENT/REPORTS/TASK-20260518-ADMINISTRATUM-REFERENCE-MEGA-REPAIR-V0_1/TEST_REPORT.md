# Test Report

## Verification Summary

- `python -m py_compile` passed for `administratum_agent_runner.py`, `administratum_dossier_factory.py`, and `administratum_v1_core.py`.
- JSON validation passed for updated schemas, samples, and `agent_manifest.json`.
- `check-all` run `RUN-ADMINISTRATUM-20260518-184654-4f05cf` completed with command status `WARN`, while `check_all_report.json` recorded `PASS 43/43`.
- The command-level WARN is intentional because the worktree is dirty with admitted task changes and internal warnings are no longer hidden under PASS.

## Key Runtime Evidence

- check-all report: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-184654-4f05cf/reports/check_all_report.json`
- schema regression: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-184633-f96489/reports/schema_regression_report.json`
- dirty admission simulation: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-184641-4efb67/reports/collect_reality_snapshot_dirty_admission_report.json`
- recent parser proof: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185157-32a9b5/reports/recent_runs_report.json`
- status JSON sample: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185128-7ab2aa/reports/status_report.json`
- KPD scorecard output: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185128-cd11a4/reports/kpd_score.json`
- no-PDF dossier build: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185524-182acc/reports/dossier_factory_build_report.json`
- no-PDF dossier verify: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185531-3b3a05/reports/dossier_verify_report.json`
- tampered hash verify: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185609-4e42b6/reports/dossier_verify_report.json`
- post-dossier schema regression: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185615-185e48/reports/schema_regression_report.json`
- final repair dossier verify: `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-REFERENCE-MEGA-REPAIR-20260518-215846/repair_dossier/FINAL_REPAIR_DOSSIER_VERIFY.json`

## Focus Checks

| Check | Result |
|---|---|
| valid freelance envelope | PASS |
| malformed freelance envelope | BLOCKED |
| build freelance handoff | PASS |
| `/shell` inside shell | PASS, `already_in_shell` |
| shell typo `/soctor-oss` | PASS, suggested `/doctor-oss` |
| dirty-state simulation | OWNER_DECISION_REQUIRED |
| recent parser | PASS, parsed recent command/status/warnings refs |
| schema regression | WARN, legacy old PDF dossier detected until new no-PDF dossier is built |
| post-dossier schema regression | PASS |
| build-dossier no-PDF default | WARN, only due admitted dirty/missing optional legacy reports |
| verify-dossier --latest | PASS |
| tampered hash check | FAIL as expected |
| final repair dossier no-PDF/SHA | PASS |

## Dossier Proof

New dossier ZIP:

`IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-ADMINISTRATUM-20260518-185524-182acc/dossier_factory/ADMINISTRATUM_DOSSIER_TASK-20260518-ADMINISTRATUM-REFERENCE-MEGA-REPAIR-V0_1.zip`

Verifier result: `PASS`, `default_dossier_has_pdf: false`, `pdf_members: []`, `hash_verification.ok: true`.
