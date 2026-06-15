# NEXT TASK IMPROVEMENT REPORT

## KPD verdict
KPD_PLUS

## What made this task harder
- phase evidence is spread across many report folders with mixed naming conventions.
- local-file browser constraints make direct JSON loading inconsistent across browsers.
- authority ACK files are partially canonical and partially draft/skeleton.

## Required questions
1. What made this task harder than necessary?
- distributed phase evidence paths and inconsistent report naming.
2. What should New Generation add/change before the next task?
- add a canonical phase registry index JSON for phases 1-10.
3. Which organ should own that improvement?
- Administratum + Astronomicon.
4. Which contract/schema/validator should be added?
- `SANCTUM_NG_PHASE_REGISTRY_V0_1.schema.json` + validator for required evidence path coverage.
5. Which context should move from prompt into organs?
- phase route mapping and canonical report-path conventions.
6. What should Officio define better?
- stable owner-response language split and concise final closure template for all VM contours.
7. What should Doctrinarium enforce better?
- authoritative non-skeleton role contract for doctrine checks in NewGen.
8. What should Mechanicus automate/validate?
- unified builder+validator runner that also emits final receipt and changed-file status.
9. What should Astronomicon structure better?
- deterministic taskpack->phase map pointer bundle to avoid repeated discovery.
10. What should Administratum remember better?
- latest validated report folder per phase and latest receipt pointers.
11. What should Sanctum show better?
- consistent in-app warning taxonomy and evidence deep-links per phase.
12. What can be done immediately within same context window before next task?
- add a thin CLI wrapper to run builder+validator+report refresh in one bounded command.

## What should be moved from prompt into organs
- canonical NewGen phase IDs + evidence path catalog.
- required closure checklist (commit/push/verify/clean) as reusable gate checklist artifact.

## Organ ownership recommendations
| Improvement | Owner organ | Reason | Proof required |
|---|---|---|---|
| Canonical phase registry index | Administratum | stable path/evidence discovery | schema + validator pass |
| Taskpack phase map embed | Astronomicon | lower context overhead | task formation output includes map |
| Non-skeleton doctrinarium role contract | Doctrinarium | remove WARN-only authority state | role contract status upgraded from skeleton |
| One-shot bounded truth refresh runner | Mechanicus | reduce manual command sequence | deterministic CLI receipt |
| Unified RU/EN owner UI labels policy package | Sanctum | enforce bilingual consistency | i18n resource contract and audit |

## What to do before the next task
1. Add `SANCTUM_NG_PHASE_REGISTRY_V0_1` contract + sample index.
2. Add `sanctum_ng_refresh_runner.py` to run builder/validator and refresh report sections.
3. Promote Doctrinarium role contract from skeleton to foundation-ready with explicit gate links.

## Suggested next task
`TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-RUNNER-VM3-V0_1`

## Context discipline result
OK
