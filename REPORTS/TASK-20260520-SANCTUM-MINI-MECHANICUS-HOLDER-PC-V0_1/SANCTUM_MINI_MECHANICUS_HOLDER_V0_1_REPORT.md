# SANCTUM MINI MECHANICUS HOLDER V0.1 REPORT

Task: `TASK-20260520-SANCTUM-MINI-MECHANICUS-HOLDER-PC-V0_1`
Generated: `2026-05-20T04:58:57.959596+00:00`

## Outcome

- Local server: PASS
- API health/state/mechanicus endpoints: PASS
- Dashboard HTML load: PASS
- Mechanicus adapter (real data): PASS
- Placeholder/locked truth semantics: PASS
- Owner actions safety mode: WARN (display/copy only)
- Browser screenshot capture: WARN (HTML capture used)
- Commit/push policy: PASS (no commit, no push)

## Key truth values

- Mechanicus status: `CONNECTED`
- Connected organs: `1`
- Placeholders: `7`
- Locked: `2`
- Warnings: `1`
- Errors: `0`
- Blockers: `0`

## Evidence links

- `SERVER_SMOKE_TEST_LOG.md`
- `API_HEALTH_SAMPLE.json`
- `API_STATE_SAMPLE.json`
- `API_MECHANICUS_SAMPLE.json`
- `DASHBOARD_HTML_CAPTURE.html`
- `OWNER_LAYOUT_MAPPING.md`
- `MECHANICUS_ADAPTER_REPORT.md`
- `FAKE_GREEN_GUARD_REPORT.md`
- `VISUAL_GAP_REPORT.md`

## Owner clarification applied

- First left screenshot was accidental and excluded from accepted evidence.

## Verdict

`PASS_WITH_WARNINGS_OWNER_REVIEW_READY_NO_COMMIT`
