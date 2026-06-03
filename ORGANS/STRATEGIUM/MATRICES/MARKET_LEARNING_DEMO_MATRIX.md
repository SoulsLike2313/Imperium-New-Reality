# MARKET_LEARNING_DEMO_MATRIX

Status: `CANDIDATE_NOT_CANON`
Seed status: `CANDIDATE_SEED`
Owner organ: `Strategium`
Support organs: `Mechanicus, Inquisition, Administratum`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/MATRICES/MARKET_LEARNING_DEMO_MATRIX.md`

## Purpose
Future domain seed for market/trading learning on demo-only boundaries.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| MLD-01 | Market experiments stay demo-only until readiness unlock. | No real-money risk during learning phase. | Inquisition | Strategium, Mechanicus | demo-boundary policy; cap receipts | All market actions are simulated/demo and clearly marked. | Demo scope exists but enforcement tooling is pending. | Any real-money claim appears before unlock. | CANDIDATE_SEED | Create demo-account readiness checklist with API sandbox boundaries. |

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
