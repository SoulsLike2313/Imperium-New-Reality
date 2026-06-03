# Sanctum Mini API Dashboard V0.3

Local, truth-first dashboard with **LIVE terminal center viewport** for the single connected organ: `MECHANICUS_AGENT`.

## Scope

- Python stdlib local server (`http.server`).
- Browser dashboard (`HTML/CSS/JS`).
- Real Mechanicus adapter from repo data.
- Honest placeholders for non-connected organs.
- Locked placeholders for `CUSTODES` and `THRONE`.
- No fake green status.
- No arbitrary shell from browser/API.

## Run

```powershell
cd E:\IMPERIUM
python IMPERIUM_NEW_GENERATION\SANCTUM_MINI\server.py --host 127.0.0.1 --port 8765
```

Open:

- `http://127.0.0.1:8765/`

## API Endpoints

- `GET /api/health`
- `GET /api/state`
- `GET /api/organs`
- `GET /api/mechanicus`
- `GET /api/mechanicus/screenshots`
- `GET /api/mechanicus/reports`
- `GET /api/actions`
- `POST /api/actions/run`
- `GET /api/actions/history`
- `POST /api/terminal/execute`
- `GET /api/terminal/history`
- `GET /api/mechanicus/screenshot/latest`

## Terminal Safety

Manual terminal input is mapped to a strict server-side allowlist only:

- `status`
- `tools`
- `check`
- `identity`
- `where`
- `help`
- `raw`
- `screenshot`
- `clear`

Everything else returns `BLOCKED_NOT_ALLOWLISTED`.

## Bilingual UI

RU/EN switch is built into the dashboard UI.
Machine artifacts and API field keys remain English.
