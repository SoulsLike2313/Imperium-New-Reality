# CENTER_VIEWPORT_UX_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-MECHANICUS-LIVE-TERMINAL-PC-V0_3
- generated_at_utc: 2026-05-20T11:28:33.5880699Z

## V0.3 center behavior

- Default active center tab: LIVE.
- LIVE header renders MECHANICUS_AGENT :: LIVE TERMINAL.
- LIVE panel includes:
  - scrolling output stream
  - status/safety/exit/duration/timestamp metadata
  - manual command input + run/clear controls
- EVIDENCE tab contains screenshot preview (/api/mechanicus/screenshot/latest).
- REPORTS tab contains latest report/screenshot/receipt path summaries.
- RAW JSON tab shows API truth payload preview.
- ACTION HISTORY tab shows executed/blocked actions.

## Owner correction alignment

PASS: screenshot/evidence preview is no longer the default center content.
