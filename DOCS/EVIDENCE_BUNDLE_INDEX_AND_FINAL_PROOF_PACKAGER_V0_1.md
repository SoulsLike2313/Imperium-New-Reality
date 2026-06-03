# Evidence Bundle Index and Final Proof Packager V0.1

Status: CANDIDATE_V0_1
Owner organ: ADMINISTRATUM
Support organs: MECHANICUS, INQUISITION, OFFICIO_AGENTIS

## Purpose

Prevent final closure gaps where evidence exists near a bundle but is not indexed, hashed, or replayable.

## Required Evidence Index Fields

An evidence index must record:

- task_id
- final_head
- remote_head
- bundle_path
- bundle_sha256
- required_receipts present or missing
- self_reference_limit
- reviewer_gaps
- next_gate

## Required Final Proof Receipt Fields

A final closure proof receipt must record:

- task_id
- local_head
- remote_head
- origin_master_equals_head
- worktree_clean
- bundle_path
- bundle_sha256
- self_reference_limit
- verdict

## Self-Reference Limit

A committed receipt cannot fully prove the commit hash that will contain that same receipt before the commit exists. The final Owner response and a no-write post-push verification command must provide the exact final local HEAD and remote HEAD equality proof.

## Bundle Rule

The bundle is not a substitute for receipts. The bundle must be indexed and hashed, and sha256sums.txt must record the bundle hash or explicitly record the self-reference limitation.

## Builder

Use:

```text
python TOOLS/EVIDENCE/build_evidence_index_v0_1.py --task-id <TASK_ID> --report-dir REPORTS/<TASK_ID>
```

The builder is New Reality root-bound and does not read parent folders or Ancient Empire.

