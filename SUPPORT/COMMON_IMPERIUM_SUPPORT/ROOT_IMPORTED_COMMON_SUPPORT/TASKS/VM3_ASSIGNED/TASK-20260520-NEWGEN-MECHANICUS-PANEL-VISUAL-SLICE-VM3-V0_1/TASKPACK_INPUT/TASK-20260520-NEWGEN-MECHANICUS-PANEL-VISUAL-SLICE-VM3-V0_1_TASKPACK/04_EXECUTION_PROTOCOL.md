# Execution protocol

## Phase -1 — Officio authority intake

Complete `09_OFFICIO_AUTHORITY_INTAKE_GATE.md`.

## Phase 0 — Start ack and Git truth

Create:
`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-MECHANICUS-PANEL-VISUAL-SLICE-VM3-V0_1/START_ACK.md`

Also save:
- `GIT_STATUS_BEFORE.txt`

## Phase 1 — Read topology + assets

Read:
- V0.2R topology files relevant to Mechanicus panel
- owner visual contract
- asset index
- included PNG references

Create `WORK_LOG.md` notes:
- what is useful from topology
- what visual cues are extracted from target reference
- what must be avoided from old/current rough implementations

## Phase 2 — Build isolated slice

Implement the isolated slice under:
`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`

## Phase 3 — Add small state logic

Implement minimal data/state presentation:
- active / idle / warn / blocked / unknown
- static or mock-backed is allowed if honest

## Phase 4 — Screenshot evidence

Produce:
- 1 full screenshot
- 2-4 detail screenshots/crops

## Phase 5 — Reports

Create:
- `REPORTS/IMPLEMENTATION_REPORT_EN.md`
- `REPORTS/OWNER_REPORT_RU.md`
- `RECEIPTS/FINAL_RECEIPT.json`

## Phase 6 — Commit/push

Before commit:
- run `git status --short`
- inspect `git diff --stat`
- ensure forbidden write roots are untouched

Commit message suggestion:
`TASK-20260520: implement Mechanicus panel visual slice v0_1`
