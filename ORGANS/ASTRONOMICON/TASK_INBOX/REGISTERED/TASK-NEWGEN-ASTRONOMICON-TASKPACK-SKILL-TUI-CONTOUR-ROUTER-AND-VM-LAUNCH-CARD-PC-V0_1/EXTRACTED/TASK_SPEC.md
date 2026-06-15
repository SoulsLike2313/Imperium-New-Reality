# Task Spec

Task ID: `TASK-NEWGEN-ASTRONOMICON-TASKPACK-SKILL-TUI-CONTOUR-ROUTER-AND-VM-LAUNCH-CARD-PC-V0_1`

Title: Astronomicon Taskpack Registration Skill TUI contour router and VM launch card.

Target contour: PC.

Owner start message: `start task`.

Baseline accepted head: `a67cc8b5e2082b7515cbc7028bfc81917d16ff42`.

## Intent

Build the first working Astronomicon-owned Taskpack Registration Skill. The Owner must be able to open an Astronomicon TUI or command interface, choose a taskpack ZIP from Downloads or any path, choose a target contour, and let Astronomicon perform registration through the correct contour route.

The term is Skill, not launcher. This capability is an agent hand owned by Astronomicon. IDE may later call it as a button or panel, but IDE must not become the truth source.

## Required contour behavior

PC contour:

- Select or provide ZIP path.
- Read TASK_ID and step name from root MANIFEST.json.
- Run local Astronomicon intake.
- Run local Astronomicon resolver.
- Block with a readable reason if intake or resolver fails.
- Display a local launch card with STEP, TASK_ID, registered task path, TASKPACK path and the exact message `start task`.

VM3 and VM2 contours:

- Select or provide ZIP path on PC.
- Send ZIP to target contour inbox.
- Sync target contour repo to accepted origin/master HEAD with safe checks.
- Run Astronomicon intake on the target contour.
- Run Astronomicon resolver on the target contour.
- If PASS or PASS_WITH_WARNINGS, open a GUI terminal on the target VM with STEP, TASK_ID, registered task path, TASKPACK path and exact copyable `start task`.
- If the route is unavailable, write BLOCK/WARN evidence and do not fake PASS.

## Required implementation location

Preferred path:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/`

Suggested files:

- `SKILL_MANIFEST.json`
- `README.md`
- `astronomicon_taskpack_registration_skill_v0_1.py`
- `contour_route_config.example.json`
- `schemas/*.schema.json`
- `tests/*.py` or smoke scripts if the repo already uses that form
- `reports/*.json` for local receipts if appropriate

Do not scatter implementation across unrelated zones.

## Required naming decision

Use `Skill` in docs, manifests and Owner-facing descriptions. Do not canonize `launcher` as the primary term. It may appear only as a compatibility alias if needed.

## Main deliverable

A minimal working Skill, not a full IDE feature. It may be text TUI or menu-driven CLI for v0.1, as long as it is reliable, evidence-producing and callable later by IDE.
