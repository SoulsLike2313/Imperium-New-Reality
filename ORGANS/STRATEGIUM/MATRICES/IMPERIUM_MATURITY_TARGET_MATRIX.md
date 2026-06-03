# IMPERIUM_MATURITY_TARGET_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Strategium`
Support organs: `Astronomicon, Inquisition, Mechanicus, Administratum`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/MATRICES/IMPERIUM_MATURITY_TARGET_MATRIX.md`

## Purpose
Defines target maturity trajectory from synthetic form to controlled real-use execution across all corridors.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| IMT-01 | Task-entry corridor is deterministic and resolves from TASK_ID + start task. | Predictable execution entry without long prompts. | Astronomicon | Officio Agentis, Mechanicus, Inquisition | resolver_positive_proof_receipt.json; resolver_negative_fixture_report.md | Registered task and current expected task both resolve with complete route/start evidence. | Resolves only in synthetic fixtures or with known caps. | Resolver cannot deterministically resolve canonical task entry. | WARN | Close remaining resolver caps in first manual Logos registration trial. |
| IMT-02 | Real-use pilot has explicit preflight gate and reviewers. | No accidental launch without readiness discipline. | Strategium | Inquisition, Administratum, Astronomicon | real_use_pilot_preflight_report.md; REAL_USE_PILOT_READINESS_MATRIX.md | Pilot readiness criteria are measurable and reviewer responsibilities assigned. | Criteria exist but not all evidence is populated yet. | Pilot readiness has no measurable gate. | WARN | Run first preflight closure without executing real pilot runtime. |
| IMT-03 | Future domains are preserved as non-active maturity seeds. | Ideas are retained without fake capability claims. | Strategium | Mechanicus, Schola Imperialis, Inquisition | maturity_matrix_seed_report.md; future-domain matrix seed files | All seed domains are present and marked CANDIDATE_SEED. | Seeds exist but some criteria remain UNKNOWN. | Future domains are missing or overclaimed as active. | PASS | Connect each seed to one safe pilot backlog item. |

## PASS/WARN/BLOCK Summary
PASS when all mandatory criteria are PASS or explicit WARN-with-cap with no BLOCK criteria.
WARN when criteria are partially met but no blocking contradiction exists.
BLOCK when any blocking criterion is triggered or capability overclaim appears.

## Fake-Green Flags
- CLAIM_WITHOUT_REPLAY
- AGENT_REASONING_AS_SYSTEM_CAPABILITY
- STALE_RECEIPT
- DIRTY_STATE_HIDDEN
- OWNER_DECISION_MISSING
