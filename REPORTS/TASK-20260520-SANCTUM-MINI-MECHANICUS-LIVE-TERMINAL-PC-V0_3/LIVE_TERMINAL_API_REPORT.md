# LIVE_TERMINAL_API_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-MECHANICUS-LIVE-TERMINAL-PC-V0_3
- generated_at_utc: 2026-05-20T11:28:33.5880699Z
- base_smoke_log: SERVER_SMOKE_TEST_LOG.md

## Implemented endpoints

- GET /api/actions
- POST /api/actions/run
- GET /api/actions/history
- POST /api/terminal/execute
- GET /api/terminal/history

## Terminal execute sample

- sample file: API_TERMINAL_EXECUTE_SAMPLE.json
- request: { "organ": "MECHANICUS_AGENT", "command": "tools" }
- result: status=PASS, source=terminal_manual, ction_id=mechanicus_visual_tools

## Terminal history sample

- sample file: API_TERMINAL_HISTORY_SAMPLE.json
- allowlist from API: status, tools, check, identity, where, help, raw, screenshot, clear
- history shows both sources:
  - 	erminal_manual
  - ction_button

## Smoke verdict

PASS: required terminal API endpoints respond and return structured safety fields.
