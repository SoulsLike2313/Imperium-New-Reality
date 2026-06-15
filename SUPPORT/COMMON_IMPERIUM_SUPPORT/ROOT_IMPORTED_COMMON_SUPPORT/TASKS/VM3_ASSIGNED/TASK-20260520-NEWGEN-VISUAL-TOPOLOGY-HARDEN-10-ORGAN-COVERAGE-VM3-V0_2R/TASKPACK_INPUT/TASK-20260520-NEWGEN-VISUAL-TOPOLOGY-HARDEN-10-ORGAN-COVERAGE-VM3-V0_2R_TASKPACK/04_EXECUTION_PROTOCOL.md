# Execution protocol

## Phase -1 — Officio authority intake

Complete `09_OFFICIO_AUTHORITY_INTAKE_GATE.md`.

No implementation before:
- `OFFICIO_ROLE_ACK_VM3_SERVITOR.json`
or
- `OFFICIO_ROLE_AUTHORITY_MISSING_WARN.json`

## Phase 0 — Start ack and Git truth

Create:

`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R/START_ACK.md`

Record:
- whoami
- hostname
- pwd
- repo root
- HEAD before work
- git status before work
- Officio intake result
- read-order confirmation

Also save:
- `GIT_STATUS_BEFORE.txt`

## Phase 1 — Inspect current topology

Inspect current Visual Foundry files and append notes to `WORK_LOG.md`.

## Phase 2 — Add 10 organ node passports

Create/update required organ node passports.

## Phase 3 — Add 10 right panel passports

Create/update right-context dock panel passports.

## Phase 4 — Repair ownership model

Normalize required ownership fields.

## Phase 5 — Registry and truth map

Update registry and truth map.

## Phase 6 — Validator V0.2

Update/run validator and save JSON report.

## Phase 7 — Reports

Create/update required reports.

## Phase 8 — Commit/push

Before commit:
- run `git status --short`
- run validator
- inspect `git diff --stat`
- ensure forbidden write roots are not touched

Commit:
`TASK-20260520: harden New Generation visual topology coverage`

Push if possible.
