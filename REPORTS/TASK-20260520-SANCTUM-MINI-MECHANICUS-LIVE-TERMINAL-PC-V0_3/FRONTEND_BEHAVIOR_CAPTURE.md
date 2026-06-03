# FRONTEND_BEHAVIOR_CAPTURE

- task_id: TASK-20260520-SANCTUM-MINI-MECHANICUS-LIVE-TERMINAL-PC-V0_3
- generated_at_utc: 2026-05-20T11:28:33.5880699Z
- validation_mode: local static source capture + API smoke data

## Captured behavior

- static/index.html defines center tabs: LIVE, EVIDENCE, REPORTS, RAW JSON, ACTION HISTORY.
- LIVE tab is marked is-active by default in HTML and JS bootstrap (setCenterTab("live")).
- static/app.js routes:
  - left action buttons -> POST /api/actions/run
  - manual input -> POST /api/terminal/execute
  - history load -> GET /api/terminal/history + GET /api/actions/history
- static/styles.css ensures terminal stream is scrollable and output is readable (.terminal-stream, .entry-stdout, .entry-stderr).

## Evidence limits

- Optional browser screenshots were not auto-captured in this run.
- Functional behavior is evidenced by API logs and source captures in this bundle.
