# SERVER SMOKE TEST LOG

started_utc: 2026-05-20T04:57:11.005202+00:00
ended_utc: 2026-05-20T04:57:14.329004+00:00
server_url: http://127.0.0.1:8765
python_compile_check: PASS

## Endpoint results

- /api/health: HTTP 200 => PASS
- /api/state: HTTP 200 => PASS
- /api/mechanicus: HTTP 200 => PASS
- /api/organs: HTTP 200 => PASS
- /api/actions: HTTP 200 => PASS
- /api/mechanicus/reports: HTTP 200 => PASS
- /api/mechanicus/screenshots: HTTP 200 => PASS
- /: HTTP 200 => PASS

## Truth assertions
- mechanicus_status: CONNECTED
- placeholders_count: 7
- locked_count: 2
- note: actions are SAFE_DISPLAY_ONLY in V0.1
