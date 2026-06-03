# PIPELINE_30_TASK_ORCHESTRATION_MATRIX

Status: `CANDIDATE_NOT_CANON`
Seed status: `CANDIDATE_SEED`
Owner organ: `Strategium`
Support organs: `Administratum, Mechanicus, Inquisition, Schola Imperialis`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/MATRICES/PIPELINE_30_TASK_ORCHESTRATION_MATRIX.md`

## Purpose
Future domain seed for high-discipline orchestration of 30+ tasks toward stable PASS_WITH_WARNINGS/PASS gating.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| P30-01 | Pipelines maintain handoff continuity and cap visibility across long chains. | Scalable campaign execution with low context-loss. | Administratum | Strategium, Schola Imperialis, Inquisition | NEXT_PIPELINE_HANDOFF receipts; claim ledger chain | Each task outputs handoff + cap state + next gate with no contradictions. | Handoffs exist but incomplete chain validation. | Pipeline claims 30+ orchestration without continuity evidence. | CANDIDATE_SEED | Create continuity checker for N-task chain integrity. |

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
