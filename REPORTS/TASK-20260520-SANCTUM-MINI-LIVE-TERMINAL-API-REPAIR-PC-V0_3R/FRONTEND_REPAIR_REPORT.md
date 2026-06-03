# FRONTEND_REPAIR_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-LIVE-TERMINAL-API-REPAIR-PC-V0_3R
- generated_at_utc: 2026-05-20T12:38:48.2900165Z

## LIVE viewport wiring

- LIVE tab default is set by bootstrap call: setCenterTab("live").
- page refresh loads terminal history via GET /api/terminal/history.
- manual command form submits to POST /api/terminal/execute.
- left action buttons submit to POST /api/actions/run.
- after both manual command and left-button action, center is forced to LIVE tab and refreshed.

## Evidence tab behavior

- Evidence tab remains separate (	abEvidence / data-center-tab="evidence").
- screenshot preview remains in Evidence panel, not default center content.

## Runtime behavior proof

- status/tools commands from manual input return PASS and are rendered in terminal stream.
- left action button run is present in action history and terminal history stream source.

Verdict: frontend LIVE contract is wired and functional.
