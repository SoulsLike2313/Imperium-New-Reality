# READ THIS FILE FIRST

Task ID: `TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R`  
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
4. Before implementation, search/read canonical Officio authority sources listed in `09_OFFICIO_AUTHORITY_INTAKE_GATE.md`.
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
   - `SEED_CONTEXT/*`
   - `SCHEMAS/*`
   - `TEMPLATES/*`
   - `RECEIPT_TEMPLATE/*`

## Artifact rule

All task artifacts must live inside the repo under:

`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R/`

Actual Visual Foundry deliverables must live under:

`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/`

## Absolute rules

- Work on VM3 only.
- Do not use VM2.
- Do not touch `ORGANS/` except read-only Officio authority intake.
- Do not write to `ORGANS/`.
- Do not touch root `SANCTUM/`.
- Do not touch `IMPERIUM_TEST_VERSION/`.
- Do not do laptop/Throne operational work.
- Do not create more visual concepts.
- Do not polish CSS.
- Do not implement final UI.
- Do not claim visual success.
- Do not fake real/connected status for stub or locked organs.
- Commit all legitimate changes directly to Git if gates pass.
- Push after commit if network/auth allows.
