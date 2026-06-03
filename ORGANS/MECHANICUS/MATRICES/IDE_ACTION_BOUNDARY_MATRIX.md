# IDE_ACTION_BOUNDARY_MATRIX

Status: `CANDIDATE_NOT_CANON`
Seed status: `CANDIDATE_SEED`
Owner organ: `Mechanicus`
Support organs: `Inquisition, Astronomicon, Officio Agentis`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/MATRICES/IDE_ACTION_BOUNDARY_MATRIX.md`

## Purpose
Future domain seed for separating real local IDE actions from web-projection smoke checks.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| IAB-01 | IDE actions are classified as local-real vs projection-smoke. | Clear trust boundary for UI claims. | Mechanicus | Inquisition, Officio Agentis | action classification receipt; semantic parity notes | Every UI claim includes action class and evidence type. | Classification exists but partial. | UI claims rely only on screenshots without semantic checks. | CANDIDATE_SEED | Add checker for screenshot-only claims. |

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

## Not Active Claims
This matrix is a candidate seed and does not authorize active runtime execution in this domain.
