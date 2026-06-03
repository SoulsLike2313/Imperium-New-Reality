# MANUAL_LOGOS_PIPELINE_REGISTRATION_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Strategium`
Support organs: `Administratum, Astronomicon, Officio Agentis, Inquisition`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/MATRICES/MANUAL_LOGOS_PIPELINE_REGISTRATION_MATRIX.md`

## Purpose
Registers manual Owner+Logos execution corridor as a first-class candidate pipeline without overclaiming automation.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| MLP-01 | Manual pipeline stages are explicitly recorded. | Chat-based work remains traceable and reusable. | Administratum | Strategium, Astronomicon | manual_logos_pipeline_registration_report.md | Record includes idea, Logos interpretation, taskpack, commit, reviews, and next pipeline decision. | Record exists but some links are pending. | No durable registration record. | PASS | Create machine schema + checker for manual corridor records. |
| MLP-02 | Manual pipeline is not overclaimed as automation. | Avoids fake automation confidence. | Inquisition | Officio Agentis | hard_red_team_verdict.json; manual_logos_pipeline_registration_report.md | All statements keep manual steps explicit. | Minor wording ambiguity but capped. | Report claims autonomous pipeline execution. | PASS | Add explicit anti-overclaim checklist in pipeline template. |

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
