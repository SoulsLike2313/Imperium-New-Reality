# FAKE_GREEN_GUARD_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-MECHANICUS-LIVE-TERMINAL-PC-V0_3
- generated_at_utc: 2026-05-20T11:28:33.5880699Z
- evidence: API_STATE_SAMPLE.json

## Organ truth snapshot

- connected_organs_count: 1
- placeholders_count: 7
- locked_count: 2

## Guard checks

- PASS: only MECHANICUS_AGENT is marked CONNECTED.
- PASS: non-connected organs remain explicit PLACEHOLDER.
- PASS: CUSTODES and THRONE remain LOCKED.
- PASS: no fake claim of multi-organ connectivity introduced.
