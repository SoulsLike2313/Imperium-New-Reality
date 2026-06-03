# REAL_USE_PILOT_READINESS_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Astronomicon`
Support organs: `Strategium, Inquisition, Administratum, Mechanicus`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/MATRICES/REAL_USE_PILOT_READINESS_MATRIX.md`

## Purpose
Defines preflight-only readiness gate for first real-use pilot without executing pilot runtime yet.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| RUP-01 | Pilot definition is explicit and distinct from synthetic fixtures. | Prevents confusion between fixture success and real-use proof. | Strategium | Astronomicon, Inquisition | real_use_pilot_preflight_report.md | Real-use pilot scope, exclusions, and review roles are documented. | Definition exists but still broad. | No explicit pilot definition. | PASS | Select one safe pilot candidate and freeze acceptance thresholds. |
| RUP-02 | Resolver and entry safety gates are satisfied before pilot start. | Pilot is not launched on unstable intake/resolver foundation. | Astronomicon | Mechanicus, Inquisition | resolver_hardening_report.md; resolver_negative_fixture_report.md | All mandatory resolver hardening negatives are reproducibly blocked. | Most cases pass but residual caps remain. | Mandatory resolver negatives are missing or non-blocking. | PASS | Add local checker that fails on regression in mandatory negatives. |
| RUP-03 | Pilot remains preflight-only until Owner explicitly unlocks execution. | Control over risk and timing of first real-use action. | Officio Agentis | Inquisition, Administratum | hard_red_team_verdict.json; final_owner_summary_ru.md | Reports explicitly state no real-use runtime executed. | Some wording risks overclaim but capped. | Any claim suggests pilot execution already happened. | PASS | Introduce explicit pilot unlock receipt template. |

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
