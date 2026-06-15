# Execution protocol

## Phase -1 — Officio authority intake
Complete `09_OFFICIO_AUTHORITY_INTAKE_GATE.md`.

## Phase 0 — Baseline capture
Create:
`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-MECHANICUS-PANEL-LUXURY-NEURO-TEXTURE-PRESSURE-VM3-V0_3/START_ACK.md`

Also save:
- `GIT_STATUS_BEFORE.txt`
- current baseline note for `de732c2...`

## Phase 1 — Review baseline vs target
Review:
- current slice implementation from commit `de732c2...`
- target shell reference
- current overview/live references
- the current result screenshot

Write in `WORK_LOG.md`:
- what is already strong;
- what still looks too cheap or shallow;
- which areas need richer materials;
- which neuro-motion layers will be added or strengthened;
- how the new version will move closer to the reference.

## Phase 2 — Enhancement pass
Enhance the existing slice in-place under:
`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`

## Phase 3 — Motion safety and polish
Ensure:
- neuro-motion is visibly present;
- motion remains ambient/cosmetic;
- reduced-motion fallback exists;
- performance remains sane.

## Phase 4 — Screenshots
Produce:
- 1 full screenshot
- 3-5 detail screenshots
- before/after comparison note

## Phase 5 — Reports
Create/update:
- `REPORTS/IMPLEMENTATION_REPORT_EN.md`
- `REPORTS/OWNER_REPORT_RU.md`
- `REPORTS/ANIMATION_NOTE.md`
- `RECEIPTS/FINAL_RECEIPT_V0_3.json`

## Phase 6 — Commit/push
Before commit:
- run `git status --short`
- inspect `git diff --stat`
- ensure forbidden write roots are untouched

Commit message suggestion:
`TASK-20260520: enhance Mechanicus panel luxury neuro texture v0_3`
