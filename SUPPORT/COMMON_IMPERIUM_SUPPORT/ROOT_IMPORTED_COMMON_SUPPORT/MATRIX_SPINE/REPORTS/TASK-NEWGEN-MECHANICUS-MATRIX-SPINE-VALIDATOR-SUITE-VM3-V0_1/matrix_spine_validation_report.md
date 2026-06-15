# Matrix Spine Validation Report — TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-VALIDATOR-SUITE-VM3-V0_1

Timestamp (UTC): 2026-05-29T22:47:21Z

## Summary
- Matrix files scanned: 29
- Matrix parse failures: 0
- FAIL: 0
- WARN: 4
- INFO: 0
- Verdict: PASS_WITH_WARNINGS

## Negative Fixture Evidence
- matrix payload metadata check: expected `MATRIX_OWNER_MISSING` -> detected
- matrix status vocabulary check: expected `MATRIX_STATUS_INVALID` -> detected
- red-team schema required key check: expected `RED_TEAM_SCHEMA_REQUIRED_MISSING` -> detected

## Findings
- [WARN] MATRIX_STATUS_NONCANON_ALIAS: current_status uses non-canonical alias vocabulary. (/home/vboxuser3/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/MATRICES/TASK_FOCUS_PACKET_MATRIX.json)
- [WARN] MATRIX_STATUS_NONCANON_ALIAS: current_status uses non-canonical alias vocabulary. (/home/vboxuser3/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/MATRICES/CLAIM_LEDGER_MATRIX.json)
- [WARN] MATRIX_STATUS_NONCANON_ALIAS: current_status uses non-canonical alias vocabulary. (/home/vboxuser3/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/MATRICES/LLM_HARNESS_INTERFACE_MATRIX.json)
- [WARN] MATRIX_STATUS_NONCANON_ALIAS: current_status uses non-canonical alias vocabulary. (/home/vboxuser3/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/MATRICES/LLM_FORCE_FOCUS_MATRIX.json)

## Replay
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
- `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`

