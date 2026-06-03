# ACTION_SECURITY_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-LIVE-TERMINAL-API-REPAIR-PC-V0_3R
- generated_at_utc: 2026-05-20T12:38:48.2900165Z

## Security contract

No arbitrary shell from browser/API.

Manual input allowlist:
- status
- tools
- check
- identity
- where
- help
- raw
- screenshot
- clear

Server-side mapping is static and bounded in pi/actions.py.

## Block sample

- command: git status
- status: BLOCK
- safety: BLOCKED_NOT_ALLOWLISTED
- stderr: Command is not in the Mechanicus terminal allowlist.

Verdict: allowlist gate active, unsafe commands blocked.
