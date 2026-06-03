# LLM_HARNESS_AND_RESOURCE_CONTROL_MATRIX

Status: `CANDIDATE_NOT_CANON`
Seed status: `CANDIDATE_SEED`
Owner organ: `Mechanicus`
Support organs: `Officio Agentis, Inquisition, Administratum`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/MATRICES/LLM_HARNESS_AND_RESOURCE_CONTROL_MATRIX.md`

## Purpose
Future domain seed for LLM harness limits, context budgets, and token/resource control.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| LHR-01 | LLM runs have explicit context manifest and budget controls. | Stable cost and leakage boundaries. | Mechanicus | Officio Agentis, Inquisition | context manifest; resource receipt; red-team leakage check | Runs include manifest + budget + post-run receipt. | Manual budget declared but no checker yet. | No resource boundary for LLM harness claim. | CANDIDATE_SEED | Prototype harness receipt schema for manual Logos and Servitor modes. |

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
