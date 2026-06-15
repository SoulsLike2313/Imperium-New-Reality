# ACTION_ENDPOINTS_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-ACTIONS-VISUAL-POLISH-PC-V0_2
- generated_at_utc: 2026-05-20T05:49:50.3890521Z
- endpoint /api/actions: PASS
- endpoint /api/actions/run: PASS
- endpoint /api/actions/history: PASS
- allowlist block probe: PASS (not_allowlisted_test => BLOCK)

## Required action IDs presence

- refresh_state: PASS
- mechanicus_visual_status: PASS
- mechanicus_visual_tools: PASS
- mechanicus_visual_check: PASS
- mechanicus_visual_identity: PASS
- mechanicus_screenshot_all: PASS
- mechanicus_screenshot_command: PASS
- open_or_show_latest_report: PASS
- open_or_show_screenshots_folder: PASS
- show_api_state_json: PASS
- show_api_mechanicus_json: PASS

## Executed action smoke results

- refresh_state: status=PASS, exit_code=0, safety=ALLOWLISTED_LOCAL_NO_SIDE_EFFECTS
- mechanicus_visual_status: status=PASS, exit_code=0, safety=ALLOWLISTED_LOCAL_READ_ONLY
- mechanicus_visual_tools: status=PASS, exit_code=0, safety=ALLOWLISTED_LOCAL_READ_ONLY
- mechanicus_visual_check: status=PASS, exit_code=0, safety=ALLOWLISTED_LOCAL_READ_ONLY
- mechanicus_visual_identity: status=PASS, exit_code=0, safety=ALLOWLISTED_LOCAL_READ_ONLY
- mechanicus_screenshot_command: status=PASS, exit_code=0, safety=DISPLAY_ONLY_SAFE_FALLBACK
- open_or_show_latest_report: status=PASS, exit_code=0, safety=DISPLAY_ONLY_SAFE_FALLBACK
- open_or_show_screenshots_folder: status=PASS, exit_code=0, safety=DISPLAY_ONLY_SAFE_FALLBACK
- show_api_state_json: status=PASS, exit_code=0, safety=ALLOWLISTED_LOCAL_NO_SIDE_EFFECTS
- show_api_mechanicus_json: status=PASS, exit_code=0, safety=ALLOWLISTED_LOCAL_NO_SIDE_EFFECTS

## Safety

- Arbitrary shell action execution from API/UI is blocked.
- Only allowlisted action_id values are executable.
- Fallback display actions return paths/commands without unsafe OS-open behavior.
