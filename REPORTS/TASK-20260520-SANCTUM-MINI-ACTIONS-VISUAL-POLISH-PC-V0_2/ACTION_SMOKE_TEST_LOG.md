# Action Smoke Test Log

- started_at_utc: 2026-05-20T05:46:19.1884512Z
- GET /api/health: PASS status=WARN
- GET /api/state: PASS schema=SANCTUM_MINI_STATE_V0_2
- GET /api/mechanicus: PASS
- GET /api/actions: PASS actions_count=11
- POST /api/actions/run [refresh_state]: status=PASS exit_code=0
- POST /api/actions/run [mechanicus_visual_status]: status=PASS exit_code=0
- POST /api/actions/run [mechanicus_visual_tools]: status=PASS exit_code=0
- POST /api/actions/run [mechanicus_visual_check]: status=PASS exit_code=0
- POST /api/actions/run [mechanicus_visual_identity]: status=PASS exit_code=0
- POST /api/actions/run [mechanicus_screenshot_command]: status=PASS exit_code=0
- POST /api/actions/run [open_or_show_latest_report]: status=PASS exit_code=0
- POST /api/actions/run [open_or_show_screenshots_folder]: status=PASS exit_code=0
- POST /api/actions/run [show_api_state_json]: status=PASS exit_code=0
- POST /api/actions/run [show_api_mechanicus_json]: status=PASS exit_code=0
- POST /api/actions/run [not_allowlisted_test]: status=BLOCK expected=BLOCK
- GET /api/actions/history: PASS history_count=11
- finished_at_utc: 2026-05-20T05:46:26.7263601Z
