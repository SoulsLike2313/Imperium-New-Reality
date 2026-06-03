# API_AND_TOOL_INTEGRATION_MATRIX

Status: `CANDIDATE_NOT_CANON`
Seed status: `CANDIDATE_SEED`
Owner organ: `Mechanicus`
Support organs: `Administratum, Inquisition, Strategium`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/MATRICES/API_AND_TOOL_INTEGRATION_MATRIX.md`

## Purpose
Future domain seed for registering external APIs/tools with safety and replay requirements.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| ATI-01 | Every external API/tool has owner, risk class, and replay pattern. | Controlled expansion of integrations. | Mechanicus | Inquisition, Administratum | tool card; BOM-lite entry; negative fixture | Integration request cannot proceed without registration fields. | Registration exists but replay command missing. | Unregistered API/tool used in capability claim. | CANDIDATE_SEED | Create API registration template aligned with TOOL_SCORECARD_BOM_LITE. |

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
