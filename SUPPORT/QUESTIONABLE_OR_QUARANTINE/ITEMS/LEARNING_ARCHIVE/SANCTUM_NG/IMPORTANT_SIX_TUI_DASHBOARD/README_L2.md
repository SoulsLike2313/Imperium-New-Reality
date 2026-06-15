# Important Six Dashboard L2

Task: `TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1`

This slice upgrades Important Six dashboard from L1 snapshots into L2 safe controls:

- dashboard buttons -> allowlisted API handlers -> action receipts -> last result + history;
- owner intent and diff decision capture;
- bounded transfer dry-run intents;
- scoped writes only inside `IMPERIUM_NEW_GENERATION`.

## Launch

```powershell
python IMPERIUM_NEW_GENERATION\SANCTUM_NG\IMPORTANT_SIX_TUI_DASHBOARD\important_six_dashboard_server_v0_2.py --host 127.0.0.1 --port 8766
```

Open:

- `http://127.0.0.1:8766/`

## L2 API

- `GET /api/status`
- `GET /api/actions`
- `POST /api/actions/<action_id>/run`
- `GET /api/actions/<action_id>/last-result`
- `GET /api/action-history`
- `GET /api/owner-questions`
- `POST /api/owner-intent/decision`
- `GET /api/diff/status`

## Action Registry

Registry:

- `ACTIONS/important_six_dashboard_actions_registry_v0_1.json`

Required action fields:

- `action_id`
- `owner_organ`
- `label_ru`
- `description`
- `safety_class`
- `writes_allowed`
- `output_root`
- `handler`
- `dry_run_supported`
- `receipt_required`
- `dashboard_button_group`

## Smoke

API smoke:

```powershell
python IMPERIUM_NEW_GENERATION\SANCTUM_NG\IMPORTANT_SIX_TUI_DASHBOARD\TOOLS\important_six_dashboard_l2_smoke_v0_1.py --base-url http://127.0.0.1:8766
```

Playwright:

```powershell
python IMPERIUM_NEW_GENERATION\SANCTUM_NG\IMPORTANT_SIX_TUI_DASHBOARD\TESTS\playwright_dashboard_l2_actions_v0_1.py --base-url http://127.0.0.1:8766 --out-dir IMPERIUM_NEW_GENERATION\REPORTS\TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1
```

## Not Proven

- destructive controls;
- arbitrary transfer paths;
- full task registration;
- auto push/merge;
- live browser PTY;
- production orchestration.

