# READ THIS FILE FIRST

Task ID: `TASK-20260520-NEWGEN-MECHANICUS-PANEL-LUXURY-NEURO-TEXTURE-PRESSURE-VM3-V0_3`
Execution contour: VM3 through SSH / VS Code Remote
Repo root on VM3: `/home/vboxuser3/IMPERIUM_WORK/Imperium-`
Allowed write scope: `IMPERIUM_NEW_GENERATION` only
Commit/push: required if gates pass
External/local task folder: forbidden

## Critical authority rule

**This taskpack is NOT role authority.**

This taskpack only:
1. describes the task;
2. defines task-specific scope/gates/evidence;
3. provides addresses where canonical role/settings/response-contract authority must be read;
4. requires an Officio ACK or missing-authority WARN/BLOCK report before implementation.

## First action sequence

1. Read this file completely.
2. Read `00_START_MESSAGE_FOR_SERVITOR.txt`.
3. Read `09_OFFICIO_AUTHORITY_INTAKE_GATE.md`.
4. Before implementation, search/read canonical Officio authority sources listed there.
5. Produce `OFFICIO_ROLE_ACK_VM3_SERVITOR.json` or `OFFICIO_ROLE_AUTHORITY_MISSING_WARN.json`.
6. Only after that, read the remaining task files in order:
   - `README.md`
   - `01_TASK_SPEC.md`
   - `02_TASK_SPEC.json`
   - `03_ACCEPTANCE_GATES.json`
   - `04_EXECUTION_PROTOCOL.md`
   - `05_SCOPE_RULES.md`
   - `06_EVIDENCE_REQUIREMENTS.md`
   - `07_EXPECTED_OUTPUTS.md`
   - `08_FINAL_REPORT_TEMPLATE_RU.md`
   - `10_OWNER_VISUAL_CONTRACT_RU.md`
   - `11_ASSET_INDEX.md`
   - `SEED_CONTEXT/*`
   - `SCHEMAS/*`
   - `TEMPLATES/*`
   - `ASSETS/*`

## What this task is

Enhance the existing Mechanicus panel slice again after commit `de732c2c13beac251c79c798fcd7e7f80999e109`.

Target visual unit:
`SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`

This is a **V0_3 luxury pressure pass**.

Main mission:
- push the slice **as close as reasonably possible to the target reference language**;
- increase **texture quality / material quality / expensive feel**;
- make **neuro-motion actually visible**;
- keep truth discipline and bounded scope.

## Important note

Owner already says:
- current result is much better;
- reference direction is almost reached;
- UX / interactivity is still weak, but deep Playwright interaction audit can happen later;
- current pressure pass is mainly about **visual quality, material richness, perceived premium quality, and visible neural life**.

## Artifact rule

All task artifacts must live inside the repo under:

`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-MECHANICUS-PANEL-LUXURY-NEURO-TEXTURE-PRESSURE-VM3-V0_3/`

Actual implementation must stay under:

`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`

## Absolute rules

- Work on VM3 only.
- Do not use VM2.
- Do not write to `ORGANS/`.
- Read-only Officio intake from `ORGANS/OFFICIO_AGENTIS/**` is allowed.
- Do not touch root `SANCTUM/`.
- Do not touch `IMPERIUM_TEST_VERSION/`.
- Do not build a whole new dashboard.
- Do not restart from scratch unless absolutely necessary.
- Do not degrade the improved version into generic dashboard styling.
- Do not fake backend truth.
- Do not make motion that implies fake real work.
- Unknown/missing sections must still be visibly marked as `UNKNOWN`, `STUB`, or `LOCKED`.
- Commit all legitimate changes directly to Git if gates pass.
- Push after commit if network/auth allows.
