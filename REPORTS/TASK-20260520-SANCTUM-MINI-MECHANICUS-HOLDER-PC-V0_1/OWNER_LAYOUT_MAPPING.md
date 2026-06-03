# OWNER LAYOUT MAPPING

Task: `TASK-20260520-SANCTUM-MINI-MECHANICUS-HOLDER-PC-V0_1`
Generated: `2026-05-20T04:58:57.959596+00:00`

| Owner Zone | Implementation | Source Binding |
|---|---|---|
| Top identity/status header | `static/index.html` (`.top-zone`, `#headerMetrics`) | `/api/health`, `/api/state.repo`, `/api/state.server` |
| Left owner action zone | `static/index.html` (`.left-zone`, `#actionList`) | `/api/actions`, `/api/commands` |
| Central organ holder zone | `static/index.html` (`.center-zone`, `#organGrid`, `#organDetails`) | `/api/organs`, `/api/mechanicus` |
| Right global truth block | `static/index.html` (`.right-zone`, `#truthBlock`) | `/api/state.global_truth` |
| Bottom micro-log strip | `static/index.html` (`.bottom-zone`, `#microLog`) | `/api/state.micro_log` |

Notes:
- Only `MECHANICUS_AGENT` is connected with real data in V0.1.
- Other organs are explicit `PLACEHOLDER`.
- `CUSTODES` and `THRONE` are explicit `LOCKED`.
