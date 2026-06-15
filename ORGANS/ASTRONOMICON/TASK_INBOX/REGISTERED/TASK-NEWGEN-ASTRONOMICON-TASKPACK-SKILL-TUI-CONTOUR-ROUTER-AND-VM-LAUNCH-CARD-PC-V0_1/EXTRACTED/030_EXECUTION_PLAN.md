# Execution Plan

## Phase 0: Truth and route preflight

- Verify current HEAD, branch, origin/master relation and worktree state.
- Verify required Astronomicon intake and resolver tools exist.
- Verify current task is registered and resolver can resolve it.
- Record `repo_truth_probe.json`.

## Phase 1: Skill skeleton

Create the Astronomicon Skill folder:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/`

Add:

- `SKILL_MANIFEST.json`.
- `README.md`.
- Python Skill entrypoint.
- Contour route config example.
- Schemas or smoke receipt templates.

## Phase 2: PC contour flow

Implement and test:

- Parse ZIP root `MANIFEST.json`.
- Extract TASK_ID and step name.
- Run local Astronomicon intake.
- Run local resolver.
- Produce local launch card.
- Write receipt.

## Phase 3: VM3 contour flow

Implement and test if route is available:

- Send ZIP through configured SSH/SCP route.
- Fast-forward sync remote repo to accepted origin/master if safe.
- Run remote intake/resolver.
- Open GUI terminal on VM3 with launch card.
- Write remote route receipt.

If VM3 route fails, write BLOCK/WARN evidence instead of fake PASS.

## Phase 4: VM2 contour flow

Implement route support through config. Test live if available. If not available, write route-missing receipt and make it clear that VM2 is supported by contract/config but not live-proven in this task.

## Phase 5: Regression fixtures

Create or record fixtures for:

- BAD_ZIP_MISSING_MANIFEST.
- BAD_ZIP_MISSING_LANGUAGE_POLICY.
- BAD_ZIP_MISSING_8_ORGAN_ROUTE.
- UNREGISTERED_TASK_ID_RESOLVE.
- VALID_8_ORGAN_TASKPACK.

These are positive protection cases, not failure noise.

## Phase 6: Validation and closure

Run syntax checks, schema checks, smoke tests and git truth probe. Produce final report and commit/push if allowed by gates.
