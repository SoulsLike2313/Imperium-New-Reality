# TASK_ENTRY_CORRIDOR_CONTRACT — Stage2.1 V0.3

Status: `CANDIDATE_NOT_CANON`
Owner organ: `ASTRONOMICON`
Mode: `ALLOW_STAGE2_WITH_WARNINGS`

## Purpose

Define the first usable Astronomicon intake corridor:
Owner provides ZIP path, Astronomicon admits/registers the taskpack, marks `NEXT_EXPECTED_TASK`, and Servitor later starts from `TASK_ID + start task`.

## Route

1. Admit ZIP via taskpack intake checks.
2. Store ZIP/extracted artifacts under `TASK_INBOX/REGISTERED/<TASK_ID>/`.
3. Update `TASK_REGISTRY/task_registry.json`.
4. Update `TASK_REGISTRY/current_expected_task.json`.
5. Build route manifest with all 8 required organs.
6. Resolve by exact `task_id` and emit resolver receipt + start ACK.
7. Block malformed admission receipt, unsafe registered paths, manifest mismatch, and root `_TASKPACK_INBOX` canonical misuse.

## Forbidden claims

- No clean PASS for Stage2.
- No WARP / real runtime / freelance readiness claim.
- No visual IDE implementation claim.
- No capability claim without script/checker evidence.
