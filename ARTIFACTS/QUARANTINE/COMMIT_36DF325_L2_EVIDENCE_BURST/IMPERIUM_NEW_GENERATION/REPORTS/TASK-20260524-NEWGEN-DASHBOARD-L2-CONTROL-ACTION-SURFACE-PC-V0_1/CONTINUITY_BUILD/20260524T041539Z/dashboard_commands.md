# Dashboard Commands

Launch:
`python IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/important_six_dashboard_server_v0_2.py --host 127.0.0.1 --port 8766`

API smoke:
`python IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/TOOLS/important_six_dashboard_l2_smoke_v0_1.py --base-url http://127.0.0.1:8766`

Playwright proof:
`python IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/TESTS/playwright_dashboard_l2_actions_v0_1.py --base-url http://127.0.0.1:8766 --out-dir IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1`
