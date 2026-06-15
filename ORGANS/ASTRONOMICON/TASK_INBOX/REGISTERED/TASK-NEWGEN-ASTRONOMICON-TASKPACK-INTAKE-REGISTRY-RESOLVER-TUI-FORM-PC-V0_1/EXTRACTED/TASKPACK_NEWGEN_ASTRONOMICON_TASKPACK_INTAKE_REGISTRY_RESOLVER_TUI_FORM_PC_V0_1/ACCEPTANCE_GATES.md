# Acceptance Gates

## PASS_WITH_WARNINGS requires all

- Starting repo truth recorded.
- Ghost_Evolve V2 Entry ACK produced.
- Canonical Astronomicon task inbox/registry layout exists or equivalent is documented.
- Script-first taskpack intake tool exists.
- Task ID resolver tool exists.
- Minimal TUI/form wrapper exists.
- Taskpack admission checks MANIFEST/task_id/TASK_SPEC/ACCEPTANCE_GATES/OUTPUT_REQUIREMENTS.
- Task registry and current_expected_task are updated by positive fixture.
- Resolver finds registered task_id in positive fixture.
- Negative fixtures cover missing ZIP, bad ZIP, missing manifest, missing task_id, duplicate task_id, unsafe extraction, missing artifact.
- Task route manifest links AGENTS + Matrix Spine + all 8 organ participation packets.
- Root `_TASKPACK_INBOX` policy is stated if that folder exists or is mentioned.
- Ghost_Evolve Stage 2 learning backlog exists.
- Hard red-team verdict exists and can downgrade.
- Efficiency delta receipt exists.
- External finalization / commit-push receipts use current semantics.
- Worktree clean after push.
- Remote origin/master equals final HEAD.

## PASS_WITH_WARNINGS is expected

This is Stage 2 with inherited warnings.
Clean PASS is forbidden until real-use pilot and independent review.

## BLOCK

- No taskpack intake tool.
- No resolver.
- TUI/form does not register a ZIP.
- Task ID cannot be resolved.
- Duplicate task_id not detected.
- Unsafe extraction path not blocked.
- Route does not include 8 organs.
- Organ participation files are bypassed.
- Learning backlog missing.
- Final visual IDE started.
- WARP/real runtime/freelance readiness claimed.
- No positive efficiency delta.
- Commit/push fails.
- Worktree dirty after finalization.

## Required caps

- `CAP_ASTRONOMICON_TASKPACK_INTAKE_MISSING`
- `CAP_TASK_REGISTRY_MISSING`
- `CAP_CURRENT_EXPECTED_TASK_MISSING`
- `CAP_TASK_ID_RESOLVER_MISSING`
- `CAP_TASKPACK_ADMISSION_MISSING`
- `CAP_DUPLICATE_TASK_ID_NOT_DETECTED`
- `CAP_UNSAFE_EXTRACTION_PATH_NOT_BLOCKED`
- `CAP_ROUTE_DOES_NOT_INCLUDE_8_ORGANS`
- `CAP_TUI_FORM_NOT_FUNCTIONAL`
- `CAP_GHOST_EVOLVE_LEARNING_BACKLOG_MISSING`
- `CAP_IDE_VISUAL_STARTED_TOO_EARLY`
- `CAP_WARP_CLAIMED_WITHOUT_UNLOCK`
- `CAP_NO_EFFICIENCY_DELTA`
