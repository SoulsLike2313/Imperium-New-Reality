# Task Spec — Astronomicon Resolver Hardening, Real-Use Pilot Preflight, and Maturity Matrix Seed

Task ID: `TASK-NEWGEN-ASTRONOMICON-RESOLVER-HARDENING-REAL-USE-PILOT-PREFLIGHT-MATURITY-MATRIX-SEED-PC-V0_1`

## Background

Stage 2 created Astronomicon taskpack intake, registry, resolver, and minimal TUI form.

Known chain:
- Stage 2 bundle commit: `52418438446198649555a419f369e46822ac3458`
- Stage 2 finalization/continuity commit: `aa11980c01e545168cfb9f2420ef25ad66e5cfe8`
- Stage 1 finalization: `f10c55079274035df89ac076df2bc8cd82916a51`

Merged Logos verdict:
- Stage 2 accepted as `PASS_WITH_WARNINGS`.
- Inquisitor/Speculum adjusted delta around `+18%`.
- Astronomicon is now a task intake door, but proof remains synthetic/fixture level.
- Next task must harden resolver behavior and seed maturity matrices.

Owner strategic intent:
IMPERIUM should become a matrix-driven harness independent of the exact LLM execution mechanism. A task may be executed by Servitor, manual Logos pipeline, local/CLI Codex, future IDE ports, or later WARP agents, but it must pass through organs, matrices, receipts, caps, review, KPD/delta and learning.

## Goal

Move from "Astronomicon can register a taskpack" toward "IMPERIUM has measurable maturity criteria for real-use."

This task must:
- harden resolver behavior;
- prepare real-use pilot preflight;
- encode Owner's maturity vision into first core matrices;
- register manual Logos pipeline as a future first-class corridor;
- keep IDE visual/WARP/freelance/trading execution frozen until readiness is proven.

## Part A — Resolver hardening

Harden the Astronomicon resolver and intake edge cases.

Required negative cases:
1. missing task_id;
2. duplicate task_id;
3. registry exists but extracted task artifact missing;
4. current_expected_task points to missing task;
5. route manifest missing;
6. route manifest does not include all 8 organs;
7. malformed admission receipt;
8. unsafe registered path / path traversal;
9. task_id exists in extracted manifest but mismatch with registry;
10. start task requested without task_id;
11. root `_TASKPACK_INBOX` used as canon instead of Astronomicon registered task path;
12. corrupt registry JSON.

Required positive proof:
- valid registered task resolves;
- current expected task resolves;
- resolver returns ZIP path, extracted path, route manifest path, admission receipt path;
- start ACK can be created and includes all 8 organs.

## Part B — Real-use pilot preflight

Do not execute the real-use pilot yet.

Create a preflight form that answers:

- what counts as real-use pilot;
- what must be true before running it;
- how it differs from synthetic fixtures;
- what Owner must do;
- what Servitor must prove;
- what Inquisitor/Speculum must review;
- what delta/KPD must be measured.

Required matrix:
`REAL_USE_PILOT_READINESS_MATRIX`

Required future pilot candidates:
- small useful repo/report/tooling task;
- synthetic freelance task;
- manual Logos pipeline registration trial.

## Part C — Core maturity matrices

Create or update these matrices under an appropriate Matrix Spine / Strategium / Astronomicon location:

1. `IMPERIUM_MATURITY_TARGET_MATRIX`
2. `ASTRONOMICON_TASK_ENTRY_MATURITY_MATRIX`
3. `REAL_USE_PILOT_READINESS_MATRIX`
4. `MANUAL_LOGOS_PIPELINE_REGISTRATION_MATRIX`

Each matrix must include:
- criteria id;
- plain-language meaning;
- owner value;
- owner organ;
- support organs;
- evidence required;
- PASS/WARN/BLOCK logic;
- current status;
- next improvement hook.

## Part D — Future-domain matrix seeds

Create future-domain seeds, not full implementations:

1. `FREELANCE_CORRIDOR_MATURITY_MATRIX`
2. `MARKET_LEARNING_DEMO_MATRIX`
3. `IDE_ACTION_BOUNDARY_MATRIX`
4. `API_AND_TOOL_INTEGRATION_MATRIX`
5. `LLM_HARNESS_AND_RESOURCE_CONTROL_MATRIX`
6. `PIPELINE_30_TASK_ORCHESTRATION_MATRIX`

These must remain `CANDIDATE_SEED`, not active execution claims.

They should capture Owner's target shape:
- freelance intake/decomposition/execution/delivery/presentation;
- market/trading learning on demo accounts only;
- IDE real actions vs web projection smoke-only;
- Mechanicus-registered APIs/tools;
- CLI/Codex ports and resource/token control;
- large pipelines of 30+ tasks with 100% PASS discipline.

## Part E — Manual Logos pipeline registration

Create a candidate corridor/matrix for the work Owner and Logos do in chat.

This must record that manual Logos pipeline can be a legitimate execution/adjudication mechanism if registered:

- Owner idea captured;
- Logos interpretation captured;
- taskpack generated;
- Servitor commit linked;
- Inquisitor/Speculum review linked;
- next pipeline chosen;
- matrix/learning updates created.

Do not overclaim automation.

## Part F — Ghost_Evolve learning

Every gap found during resolver/matrix work must create a learning item:

- matrix update candidate;
- organ gap record;
- Schola lesson;
- Strategium roadmap note;
- Inquisition cap candidate;
- Mechanicus tool/checker need;
- Astronomicon route improvement.

## Allowed scope

Prefer:
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/**`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/SCHOLA_IMPERIALIS/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/**`
- task-specific reports/receipts

Avoid `AGENTS.md` unless absolutely necessary.

Forbidden:
- final visual IDE;
- WARP activation;
- real trading;
- real-money finance actions;
- real freelance claim;
- mass legacy receipt migration;
- broad unrelated rewrites;
- deleting old evidence without receipt;
- Throne/Custodes scope.

## Commit/push

PC Servitor must commit and push admitted diffs.
If commit/push is blocked, produce BLOCK report and do not fake success.
