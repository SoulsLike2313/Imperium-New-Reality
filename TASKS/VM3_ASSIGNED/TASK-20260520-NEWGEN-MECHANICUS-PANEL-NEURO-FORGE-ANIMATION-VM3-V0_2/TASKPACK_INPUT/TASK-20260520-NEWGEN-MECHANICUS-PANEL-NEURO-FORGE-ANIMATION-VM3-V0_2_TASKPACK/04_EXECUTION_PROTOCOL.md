# Execution protocol

## Phase -1 — Officio authority intake
Complete `09_OFFICIO_AUTHORITY_INTAKE_GATE.md`.

## Phase 0 — Baseline capture
Create:
`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-MECHANICUS-PANEL-NEURO-FORGE-ANIMATION-VM3-V0_2/START_ACK.md`

Also save:
- `GIT_STATUS_BEFORE.txt`
- note current baseline commit / branch

## Phase 1 — Review current slice and references
Review:
- current slice implementation from commit `138c2df...`
- target shell reference
- current overview/live references

Write in `WORK_LOG.md`:
- what already works;
- what must become more like the reference;
- which ambient animations will be added;
- which neuro-memory cues will be introduced.

## Phase 2 — Implement enhancement pass
Enhance the existing slice in-place under:
`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`

## Phase 3 — Animation safety
Ensure:
- animations are ambient only;
- reduced-motion fallback exists;
- performance remains sane;
- no fake activity semantics.

## Phase 4 — Screenshots
Produce:
- 1 full screenshot
- 3-5 detail screenshots
- before/after comparison note

## Phase 5 — Reports
Create/update:
- `REPORTS/IMPLEMENTATION_REPORT_EN.md`
- `REPORTS/OWNER_REPORT_RU.md`
- `RECEIPTS/FINAL_RECEIPT_V0_2.json`

## Phase 6 — Commit/push
Before commit:
- run `git status --short`
- inspect `git diff --stat`
- ensure forbidden write roots are untouched

Commit message suggestion:
`TASK-20260520: enhance Mechanicus panel neuro forge animation v0_2`
