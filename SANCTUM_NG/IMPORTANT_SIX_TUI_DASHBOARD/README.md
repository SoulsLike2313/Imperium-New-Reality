# Important Six TUI API Dashboard L1

Task: `TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1`

Local read-only/semi-live dashboard for six organs:
- doctrinarium
- officio
- administratum
- astronomicon
- mechanicus
- inquisition

This slice is **L1 only**.

## Scope Boundary

- API executes only allowlisted commands from `important_six_dashboard_config_v0_1.json`.
- TUI calls are restricted to `--smoke --plain-json`.
- Query calls are restricted to `--sample`.
- No write actions, no arbitrary command execution, no production orchestration claim.

## Files

- `important_six_dashboard_server_v0_1.py`
- `important_six_dashboard_v0_1.html`
- `important_six_dashboard.css`
- `important_six_dashboard.js`
- `important_six_dashboard_config_v0_1.json`
- `TOOLS/important_six_dashboard_smoke_v0_1.py`
- `TESTS/playwright_important_six_dashboard_l1_v0_1.py`

## Launch

Linux/macOS:

```bash
python3 IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/important_six_dashboard_server_v0_1.py --host 127.0.0.1 --port 8766
```

Windows (Owner command style):

```powershell
python IMPERIUM_NEW_GENERATION\SANCTUM_NG\IMPORTANT_SIX_TUI_DASHBOARD\important_six_dashboard_server_v0_1.py --host 127.0.0.1 --port 8766
```

Open:

- `http://127.0.0.1:8766/`

## API

- `GET /`
- `GET /api/status`
- `GET /api/organs`
- `GET /api/organs/<organ>/tui-smoke`
- `GET /api/organs/<organ>/query-sample`
- `GET /api/organs/<organ>/terminal-snapshot`
- `GET /api/dashboard-state`

## Smoke

```bash
python3 IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/TOOLS/important_six_dashboard_smoke_v0_1.py --base-url http://127.0.0.1:8766
```

## Playwright Proof

This repository image has no Python Playwright package. The Playwright proof script uses Node Playwright runtime from `npx` cache and runs Chromium headless checks.

```bash
python3 IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/TESTS/playwright_important_six_dashboard_l1_v0_1.py --base-url http://127.0.0.1:8766 --out-dir IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1
```

## Not Proven

- true interactive terminals
- real-time bidirectional organ sessions
- Owner Verdict button
- write actions
- production orchestration
- final visual design
- live Servitor execution stream
