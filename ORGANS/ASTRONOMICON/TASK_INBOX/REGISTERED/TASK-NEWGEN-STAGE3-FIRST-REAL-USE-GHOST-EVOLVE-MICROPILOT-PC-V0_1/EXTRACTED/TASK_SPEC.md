# Task Spec — Stage 3 First Real-Use Ghost_Evolve Micro-Pilot

Task ID: `TASK-NEWGEN-STAGE3-FIRST-REAL-USE-GHOST-EVOLVE-MICROPILOT-PC-V0_1`

## Background

The previous cleanup task closed the dirty worktree blocker:

- dirty cleanup bundle: `7f7eb8e4a955292e8e597e3b0d390199c9ef3be2`
- finalization / accepted continuity head: `d7906a40e2a001e1d98c0f7a830739d0c09ce01d`
- cap `CAP_DIRTY_WORKTREE_UNCLASSIFIED` closed as clean.

Stage 3 is now admitted with warnings.

This task is the first real-use micro-pilot. It must prove that the new Astronomicon intake + task_id route can be used for a small useful task, not only synthetic fixtures.

## Goal

Demonstrate the first end-to-end useful task through the new IMPERIUM form:

```text
Astronomicon taskpack intake
→ task_id registration
→ Servitor starts by task_id + start task
→ resolver finds task
→ 8 organs participate
→ useful output is produced
→ receipts/review handoff are generated
→ Ghost_Evolve learning updates system memory/matrices
```

## Definition of "real-use micro-pilot"

This is not a large external real-use domain.

For this task, "real-use" means:
- Owner actually registers taskpack through Astronomicon;
- Servitor uses task_id route instead of raw prompt execution;
- output is useful for deciding the next IMPERIUM step;
- maturity matrices are exercised;
- all 8 organs participate;
- review handoff is prepared.

## Useful output

Create:

`REAL_USE_MICROPILOT_READINESS_SNAPSHOT.md`
`REAL_USE_MICROPILOT_READINESS_SNAPSHOT.json`

It must answer:
- What parts of IMPERIUM were actually used in this micro-pilot?
- Did Astronomicon intake and resolver work from task_id?
- Did all 8 organs participate?
- Which maturity matrix criteria were exercised?
- Which criteria remained seed/unproven?
- What blocks the first larger real-use pilot?
- What should be the next task?
- Is manual Logos pipeline ready to be registered as a corridor?
- What Owner action became simpler?
- What still felt manual or fragile?

## Required route proof

Create:

`ASTRONOMICON_TASK_ID_EXECUTION_PROOF.json`
`ASTRONOMICON_TASK_ID_EXECUTION_PROOF.md`

It must prove:
- task_id received;
- current_expected_task matched;
- resolver found registered task;
- route manifest found;
- extracted taskpack path found;
- AGENTS.md route acknowledged;
- Matrix Spine route acknowledged;
- all 8 organ packets read/reachable;
- start ACK produced.

## Required 8-organ runtime receipt

Create:

`EIGHT_ORGAN_PARTICIPATION_RUNTIME_RECEIPT.json`
`EIGHT_ORGAN_PARTICIPATION_RUNTIME_RECEIPT.md`

For each organ:
- what input was read;
- what decision/support it provided;
- what output/receipt/matrix/gap it produced;
- whether participation was meaningful or minimal;
- what next improvement is needed.

## Required maturity matrix exercise

Create:

`MATURITY_MATRIX_EXERCISE_REPORT.json`
`MATURITY_MATRIX_EXERCISE_REPORT.md`

Matrices to exercise:
- `IMPERIUM_MATURITY_TARGET_MATRIX`
- `ASTRONOMICON_TASK_ENTRY_MATURITY_MATRIX`
- `REAL_USE_PILOT_READINESS_MATRIX`
- `MANUAL_LOGOS_PIPELINE_REGISTRATION_MATRIX`

Future-domain seeds must remain candidate:
- `FREELANCE_CORRIDOR_MATURITY_MATRIX`
- `MARKET_LEARNING_DEMO_MATRIX`
- `IDE_ACTION_BOUNDARY_MATRIX`
- `API_AND_TOOL_INTEGRATION_MATRIX`
- `LLM_HARNESS_AND_RESOURCE_CONTROL_MATRIX`
- `PIPELINE_30_TASK_ORCHESTRATION_MATRIX`

For each criterion touched:
- status before;
- evidence from this task;
- status after;
- why it changed or stayed candidate.

## Required Ghost_Evolve learning

Create:

`GHOST_EVOLVE_STAGE3_MICROPILOT_LEARNING_BACKLOG.json`
`GHOST_EVOLVE_STAGE3_MICROPILOT_LEARNING_BACKLOG.md`

Each issue found must become:
- matrix update candidate;
- organ gap;
- Schola lesson;
- Strategium roadmap note;
- Inquisition cap candidate;
- Mechanicus checker/tool need;
- Astronomicon route improvement.

## Required runtime/output classification

Create:

`RUNTIME_OUTPUT_CLASSIFICATION.json`

Classify:
- committed canonical outputs;
- curated evidence;
- runtime ephemeral outputs;
- registered taskpack artifacts;
- anything that should remain outside canon.

Do not recreate `_TASKPACK_INBOX` as root canon. Astronomicon owns canonical task registration.

## Required reports/receipts

Recommended report root:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-STAGE3-FIRST-REAL-USE-GHOST-EVOLVE-MICROPILOT-PC-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `ASTRONOMICON_TASK_ID_EXECUTION_PROOF.json/md`
- `EIGHT_ORGAN_PARTICIPATION_RUNTIME_RECEIPT.json/md`
- `REAL_USE_MICROPILOT_READINESS_SNAPSHOT.json/md`
- `MATURITY_MATRIX_EXERCISE_REPORT.json/md`
- `RUNTIME_OUTPUT_CLASSIFICATION.json`
- `GHOST_EVOLVE_STAGE3_MICROPILOT_LEARNING_BACKLOG.json/md`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `claim_ledger.jsonl`
- `capability_split_receipt.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

## Stage 3 verdict

Allowed verdicts:
- `STAGE3_MICROPILOT_PASS_WITH_WARNINGS`
- `STAGE3_MICROPILOT_PARTIAL`
- `STAGE3_MICROPILOT_BLOCKED`

Clean PASS is forbidden until independent Inquisitor + Speculum review.

## Allowed scope

Prefer:
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/**`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/*/TASK_PARTICIPATION/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/**` for receipts/continuity only
- `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/**` for checker/tool notes only
- `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/**` for caps/red-team notes only
- `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/**` for roadmap notes only
- `IMPERIUM_NEW_GENERATION/ORGANS/SCHOLA_IMPERIALIS/**` for lessons only
- task-specific reports/receipts

Avoid `AGENTS.md` unless absolutely necessary.

Forbidden:
- visual IDE implementation;
- WARP activation;
- real trading;
- real freelance production;
- API credentials/secrets;
- broad unrelated rewrites;
- mass legacy receipt migration;
- deleting registered task evidence without receipt;
- Throne/Custodes scope.

## Commit/push

PC Servitor must commit and push admitted diffs.
If commit/push is blocked, produce BLOCK report and do not fake success.
