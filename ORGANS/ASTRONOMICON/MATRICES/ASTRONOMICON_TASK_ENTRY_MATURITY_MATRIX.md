# ASTRONOMICON_TASK_ENTRY_MATURITY_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Astronomicon`
Support organs: `Officio Agentis, Mechanicus, Inquisition, Administratum`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/MATRICES/ASTRONOMICON_TASK_ENTRY_MATURITY_MATRIX.md`

## Purpose
Measures task-entry maturity from intake through resolver and start ACK safety.

## Criteria
| Criterion ID | Plain Meaning | Owner Value | Owner Organ | Support Organs | Evidence Required | PASS Logic | WARN Logic | BLOCK Logic | Current Status | Next Improvement Hook |
|---|---|---|---|---|---|---|---|---|---|---|
| ATM-01 | Admission blocks malformed or unsafe taskpacks. | Prevents bad ZIPs and path traversal from entering canon flow. | Astronomicon | Inquisition, Mechanicus | taskpack_admission_fixture_results_stage2_1.json | Negative admission fixtures for missing/bad/unsafe/duplicate cases all BLOCK. | Some edge cases covered but not all mandatory negatives. | Unsafe or malformed admissions can pass. | PASS | Add manifest schema validation checker. |
| ATM-02 | Resolver detects canonical mismatches and provenance risk. | Avoids false starts on corrupted/mismatched registered tasks. | Astronomicon | Inquisition, Administratum | task_id_resolver_fixture_results_stage2_1.json | Resolver blocks missing artifact, route gaps, malformed receipt, unsafe paths, and manifest mismatch. | Detection exists but diagnostics are incomplete. | Resolver returns PASS when mandatory mismatch case exists. | PASS | Add compact RU diagnostics map for each blocking cap. |
| ATM-03 | Current expected task routing is reliable. | Owner can say start task without manual file hunting. | Astronomicon | Officio Agentis, Mechanicus | resolver_positive_proof_receipt.json | Resolver current expected flow returns PASS_WITH_WARNINGS and includes ACK with all 8 organs. | Current expected resolves but with inherited caps. | Current expected points to missing or non-resolvable task. | PASS | Add lifecycle policy for rotating current expected tasks. |

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
