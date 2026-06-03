# HEAD_TAXONOMY_AND_FINALIZATION_RECEIPT_V0_1

Status: `CANDIDATE_NOT_CANON`
Owner organ: `ADMINISTRATUM`
Support organs: `INQUISITION`, `MECHANICUS`

## Purpose

Define non-ambiguous head semantics across implementation, artifact, receipt, and closure commits.

## Head classes

- `subject_implementation_head`: commit where implementation changes are introduced.
- `artifact_bundle_head`: commit that first contains the report/artifact bundle.
- `receipt_finalization_head`: commit that finalizes commit/push receipt semantics.
- `closure_finalization_head`: latest verified remote head used for owner-facing closure.
- `current_remote_head`: `origin/master` after final push verification.

## Red-team snapshot rule

A hard red-team artifact may carry pre-finalization repo truth when:

- snapshot timestamp and head are explicit;
- artifact is marked historical;
- clean PASS is not derived from the stale snapshot.

## Blocking rule

It is blocking when:

- pending fields (`PENDING_COMMIT`, `PENDING_PUSH_URL`, `PENDING_FINAL_GIT_CHECK`) remain in final closure artifacts;
- stale snapshot is presented as current clean-pass truth;
- head class is ambiguous or mixed without explicit mapping.

## Required receipt fields

- `subject_implementation_head`
- `artifact_bundle_head`
- `receipt_finalization_head`
- `closure_finalization_head`
- `current_remote_head`
- `snapshot_classification`
- `clean_pass_allowed`
