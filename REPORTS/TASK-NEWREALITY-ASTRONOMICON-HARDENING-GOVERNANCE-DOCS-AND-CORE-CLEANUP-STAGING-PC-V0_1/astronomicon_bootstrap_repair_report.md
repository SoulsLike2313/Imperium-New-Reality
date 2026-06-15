# Astronomicon Bootstrap Repair Report

Task: TASK-NEWREALITY-ASTRONOMICON-HARDENING-GOVERNANCE-DOCS-AND-CORE-CLEANUP-STAGING-PC-V0_1
Smoke timestamp UTC: 2026-06-07T10:35:51Z

## Summary

Astronomicon bootstrap was hardened for the active PC root. The registration skill now resolves the repository root from git or root markers, discovers current-root route config before legacy fallback, keeps PC-local routing free of remote contour dependency, and exposes a read-only discovery smoke command.

## Repairs

- Default route config path moved from the old `IMPERIUM_NEW_GENERATION` prefix to `ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/contour_route_config.json`.
- Route config discovery order is explicit: CLI override, `ASTRONOMICON_ROUTE_CONFIG`, current root operator config, legacy fallback.
- PC mode records route config discovery but does not load remote route credentials for local registration.
- Task entry library now searches current-root route/start templates before legacy fallback.
- Matrix Spine read order now uses `SUPPORT/COMMON_IMPERIUM_SUPPORT/ROOT_IMPORTED_COMMON_SUPPORT/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md` before the old root-level path.
- README and skill manifest entrypoints now point at current-root `ORGANS/...` paths and document `--discovery-smoke`.
- Repository `.gitignore` now protects the local route config and old-prefix residue from accidental staging.

## Smoke Receipt

Command: `python ORGANS\ASTRONOMICON\SKILLS\TASKPACK_REGISTRATION_SKILL\astronomicon_taskpack_registration_skill_v0_1.py --discovery-smoke`
Verdict: `PASS_WITH_WARNINGS`
Remote route attempted: `false`
Route config loaded for PC: `false`
Route config source: `current_root_operator_config`
Route config SHA256: `4ba1e09821e3f0ec4eccc48d0147475360d32b7fdf62465bd77abeba2eb9833b`

## Remaining Warnings

- Legacy fallback constants remain intentionally for diagnostic compatibility and controlled fallback.
- Old-prefix residue remains on disk and ignored; no cleanup move/delete was performed.
- Local operator config is hashed for receipt only and must not be staged.
