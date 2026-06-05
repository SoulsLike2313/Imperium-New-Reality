# Post Work Repair Loop Contract V0.2

Status: `CANDIDATE_V0_2`
Owner organ: `ADMINISTRATUM`
Support organs: `MECHANICUS`, `INQUISITION`, `CUSTODES`, `SCHOLA_IMPERIALIS`

## Purpose

The repair loop converts a blocked post-work bundle into a precise repair request. A final bundle is not accepted while any required organ receipt is missing, malformed, or reports `BLOCK`.

## Required Behavior

- Administratum validates the bundle schemas and required evidence.
- If any required organ row is missing or has `status=BLOCK`, final acceptance is blocked.
- Administratum emits `POST_WORK_REPAIR_REQUEST.json` with exact issue ids, paths, and repair actions.
- Servitor repairs only the requested defects and replays the checker.
- A repaired fixture must prove the same class of defect can move from BLOCK to PASS.

## Forbidden Behavior

- Do not summarize `PASS_WITH_WARNINGS` as clean `PASS`.
- Do not accept a bundle with missing remote proof fields.
- Do not hide a heavy artifact by ignoring it without an index entry.
- Do not claim full semantic truth, full Custodes authority, or Throne readiness.

## Acceptance Boundary

V0.2 accepts schema-backed closure path readiness only. It does not accept runtime autonomy, semantic truth, or final remote proof before post-push no-write verification.
