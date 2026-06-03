# ACTION_SECURITY_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-MECHANICUS-LIVE-TERMINAL-PC-V0_3
- generated_at_utc: 2026-05-20T11:29:22.6424256Z

## Security law enforced

No arbitrary shell from browser/API.

Manual input is mapped only to static server-side allowlist:

- status -> mechanicus_visual_status
- tools -> mechanicus_visual_tools
- check -> mechanicus_visual_check
- identity -> mechanicus_visual_identity
- where -> terminal_where (safe path summary)
- help -> terminal_help (safe static response)
- raw -> show_api_mechanicus_json
- screenshot -> mechanicus_screenshot_all or mechanicus_screenshot_command fallback
- clear -> frontend-only clear behavior

Unknown manual commands return:

- status: BLOCK
- safety: BLOCKED_NOT_ALLOWLISTED
- stderr: Command is not in the Mechanicus terminal allowlist.

## Evidence

- BLOCKED_COMMAND_PROBE_SAMPLE.json
- BLOCKED_COMMAND_PROBE_REPORT.md
