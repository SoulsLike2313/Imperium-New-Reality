# Acceptance gates

- GATE_TASK_ID_RESOLVED: Astronomicon resolver must resolve this TASK_ID before execution.
- GATE_REPO_TRUTH_PROBED: record branch, HEAD, origin/master, and dirty state.
- GATE_PREVIOUS_EVIDENCE_LOCATED: record previous Stage2 evidence paths.
- GATE_EXTERNAL_FINALIZATION_RECEIPT: create a receipt grounded in review synthesis and repo evidence.
- GATE_INDEPENDENT_REPLAY_RECEIPT: run local isolated replay or block with a precise reason.
- GATE_ADMISSION_POSITIVE_CONTROLS: preserve admission/resolver blocks as regression fixtures.
- GATE_CAP_DECISION: classify each cap as CLOSED, NARROWED, CARRIED, or BLOCKED.
- GATE_RED_TEAM: hard red-team must attack all closure claims.
- GATE_GIT_CLOSURE: commit, push, verify remote sync, and clean the worktree.
