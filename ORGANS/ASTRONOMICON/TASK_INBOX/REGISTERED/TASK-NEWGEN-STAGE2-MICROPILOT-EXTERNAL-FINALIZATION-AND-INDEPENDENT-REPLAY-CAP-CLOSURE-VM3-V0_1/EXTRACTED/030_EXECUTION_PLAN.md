# Execution plan

## Stage 0: admission and repo truth
- Resolve this TASK_ID through Astronomicon.
- Record repo head, branch, remote sync, and dirty state in `repo_truth_probe.json`.
- Read only required authority and task files.

## Stage 1: locate previous evidence
- Locate previous Stage2 micro-pilot report bundle in the repo.
- Locate context pack consumption, context economy, organ block usage, hard red-team, and commit-push receipts.
- Record paths and hashes when practical.

## Stage 2: external finalization receipt
- Use the embedded owner-provided review synthesis as the external review summary seed.
- Cross-check against repo evidence.
- Produce `external_finalization_receipt.json`.
- Mark the external-finalization cap honestly as CLOSED, NARROWED, or CARRIED.

## Stage 3: local independent replay
- Create an isolated clean temporary workspace or git worktree from the previous accepted head.
- Run the context-pack consumption harness or the smallest replayable equivalent from the previous task.
- Compare mandatory item count, missing count, broad-read detection, context economy, and output hashes where available.
- Produce `independent_replay_receipt.json`.

## Stage 4: preserve admission/resolver controls
- Record the discovered negative and positive cases as regression fixtures:
  - BAD_ZIP_MISSING_MANIFEST
  - BAD_ZIP_MISSING_LANGUAGE_POLICY
  - BAD_ZIP_MISSING_8_ORGAN_ROUTE
  - UNREGISTERED_TASK_ID_RESOLVE
  - VALID_8_ORGAN_TASKPACK
- Produce `taskpack_admission_regression_fixtures.json`.
- Produce Ghost_Evolve and Schola learning artifacts.

## Stage 5: cap decision and red-team
- Produce `cap_closure_decision.json`.
- Produce `hard_red_team_verdict.json`.
- Any clean PASS is forbidden if any target cap remains unclosed.

## Stage 6: commit and closure
- Stage only allowed artifacts.
- Commit with a task-specific message.
- Push.
- Verify origin/master equals HEAD.
- Produce `commit_push_receipt.json`.
- Leave the worktree clean.
