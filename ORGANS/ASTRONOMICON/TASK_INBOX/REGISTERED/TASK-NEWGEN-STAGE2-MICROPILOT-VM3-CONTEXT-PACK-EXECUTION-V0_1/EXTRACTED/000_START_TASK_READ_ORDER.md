# START TASK READ ORDER

Task ID: `TASK-NEWGEN-STAGE2-MICROPILOT-VM3-CONTEXT-PACK-EXECUTION-V0_1`
Target contour: `VM3`
Required starting HEAD: `cda220333299c82931f81beee461f6cb55974462`
Previous implementation anchor: `1a3d30a071f52c54fd8c8e75054caad0c5ea6f0b`

This taskpack is self-contained. The Owner should only need to attach this ZIP and write: `start task`.

Read in this order:

1. `TASKPACK_MANIFEST.json`
2. `010_TASK_BRIEF.md`
3. `020_SCOPE_LOCKS_AND_CAPS.md`
4. `030_EXECUTION_PLAN.md`
5. `040_ACCEPTANCE_CRITERIA.md`
6. `050_OWNER_FINAL_FORMAT_CONTRACT.md`
7. `INPUTS/source_state.json`
8. `INPUTS/review_synthesis.json`
9. `INPUTS/previous_task_context_pack_v0_1.json`
10. `INPUTS/previous_context_bloat_detector_receipt.json`
11. `SCHEMAS/*.schema.json`
12. `EXAMPLES/llm_focus_claim_ledger.example.jsonl`

Do not read the whole repository. The point of this task is to prove compact context-pack use.

Hard start gates:

- Confirm current repo HEAD equals `cda220333299c82931f81beee461f6cb55974462` or stop with `BLOCKED_HEAD_MISMATCH`.
- Confirm worktree is clean before edits or stop with `BLOCKED_DIRTY_START`.
- Confirm this task is registered or register it through the Astronomicon intake path if the local tool exists.
- Confirm IDE, WARP, browser automation, external API actions, freelance and trading lanes remain locked.
