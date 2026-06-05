# Post Work Bundle Contract V0.1

Status: `CANDIDATE_V0_1`
Owner organ: `ADMINISTRATUM`
Support organs: `ASTRONOMICON`, `OFFICIO_AGENTIS`, `MECHANICUS`, `DOCTRINARIUM`, `INQUISITION`, `STRATEGIUM`, `SCHOLA_IMPERIALIS`, `CUSTODES`

## Purpose

The post-work bundle is the historical delta of a completed task. A git commit is only one proof source. The bundle must preserve taskpack provenance, route evidence, file deltas, receipts, organ admission notes, validation results, local-heavy artifact policy, and remote closure proof.

## GitHub-Safe Boundary

GitHub receives index cards, receipts, hashes, and small canonical artifacts. It must not receive large screenshots, runtime dumps, private context, heavy archives, or local-only evidence unless a task explicitly justifies them.

Large or private artifacts must be represented by:

- stable local path class;
- sha256 when a file exists locally and is allowed to be hashed;
- storage policy;
- visibility policy;
- owner organ;
- reason the artifact is not committed.

## Required Bundle Evidence

Each completed task report directory should contain these GitHub-safe files:

- `POST_WORK_BUNDLE_INDEX_CARD.json`
- `POST_WORK_RECEIPT_INDEX.json`
- `POST_WORK_FILE_DELTA_INDEX.json`
- `POST_WORK_ORGAN_RING_RECEIPT.json`
- `ADMINISTRATUM_POST_WORK_BUNDLE_RECEIPT.json`
- `INQUISITION_CONTRADICTION_SCAN_RECEIPT.json`
- `CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json`
- `GIT_CLOSURE_RECEIPT.json`
- `REMOTE_CLOSURE_RECEIPT.json`
- `NEXT_TASK_ROUTE.json`
- `FINAL_OWNER_SUMMARY_RU.md` after Officio role entry

If an expected item is not implemented, it must be represented by an explicit limitation receipt with `status=NOT_YET_IMPLEMENTED`, a reason, owner organ, and next task route.

## Admission Boundary

Administratum V0.1 may claim only `POST_WORK_BUNDLE_STRUCTURAL_PASS` or `POST_WORK_BUNDLE_STRUCTURAL_BLOCK`. It does not claim full semantic truth, Custodes full admission, Inquisition full purity, or production autonomy.

## Required Checks

The checker must:

- locate the registered Astronomicon taskpack for the task id;
- verify report indexes and core receipts parse as UTF-8 JSON without BOM;
- verify all nine required organs are represented;
- block when Administratum bundle receipt is missing;
- block when Inquisition contradiction scan is missing;
- block when Custodes audit receipt is missing or malformed;
- block unindexed heavy artifacts in GitHub-safe report output;
- report post-push remote proof as pending unless exact equality evidence is supplied externally after push.
