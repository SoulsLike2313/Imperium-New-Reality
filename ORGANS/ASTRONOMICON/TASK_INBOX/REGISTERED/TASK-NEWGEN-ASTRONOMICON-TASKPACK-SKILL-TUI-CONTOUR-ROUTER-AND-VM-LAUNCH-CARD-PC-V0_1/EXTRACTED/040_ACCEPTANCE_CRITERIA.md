# Acceptance Criteria

The task is acceptable only if all required criteria below are met or explicitly blocked with evidence.

## Core Skill

- A dedicated Astronomicon Taskpack Registration Skill folder exists.
- A Skill manifest exists and identifies Astronomicon as owner.
- The Skill can be called through a short command or TUI entrypoint.
- The Skill reads TASK_ID from taskpack root MANIFEST.json.
- The Skill can register at least one taskpack on PC contour through Astronomicon intake/resolver.
- The Skill writes a receipt for every attempted contour route.

## Remote contour behavior

- VM3 route either works live or produces a precise route-missing/block receipt.
- VM2 route either works live or produces a precise route-missing/block receipt.
- For a successful VM2/VM3 registration, the target VM displays a GUI terminal launch card with STEP, TASK_ID, registered task path, TASKPACK path and exact `start task` message.
- A remote registration is not considered complete without the target VM launch-card evidence or an explicit limitation receipt.

## Safety

- The Skill blocks on intake failure.
- The Skill blocks on resolver failure.
- The Skill does not silently resolve registry conflicts.
- The Skill does not claim live remote success from a dry run.
- IDE is not a truth source.

## Evidence

- Required output files from OUTPUT_REQUIREMENTS.md exist.
- JSON files are valid.
- Python files pass syntax check.
- Git closure receipt exists.
- Final Owner summary is Russian runtime output routed through Officio.
