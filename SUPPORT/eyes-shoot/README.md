# eyes-shoot — Playwright harness for the Imperium viewer

_part of MECHANICUS → EYES-PLAYWRIGHT-HARNESS-0001_

Renders every view (V0..V6) of `SUPPORT/viewer/` to PNG via headless Chromium.
Useful for: AAA visual audits, sharing screenshots with external LLMs (Codex /
Grok / Claude), regression catching, doctrine illustration.

## One-time install

```powershell
cd <repo>\SUPPORT\eyes-shoot
.\INSTALL.ps1
```

This runs:

- `python -m pip install --upgrade playwright`
- `python -m playwright install chromium`

Downloads ~150MB of Chromium binary once. Idempotent.

## Shoot all views

```powershell
.\SHOOT.ps1
```

What happens:

1. Spins up `python -m http.server` on a free 127.0.0.1 port, rooted at repo.
2. Launches headless Chromium 1920x1200 @ scale=2 (retina).
3. For each of `V0,V1,V2,V3,V4,V5,V6`:
   - Navigates to `http://127.0.0.1:<port>/SUPPORT/viewer/?v=<V>`.
   - Waits for `window.cy.elements().length > 0` (or 60s timeout).
   - Waits an extra 3s for cose layout to settle.
   - Screenshots into `.\out\<V>.png`.
4. Tears down the local server.

Result: 7 PNGs in `.\out\`.

## Common flags

| flag         | default                  | meaning                                              |
| ------------ | ------------------------ | ---------------------------------------------------- |
| `-Views`     | `V0,V1,V2,V3,V4,V5,V6`   | comma-separated subset, e.g. `"V0,V2"`               |
| `-ViewerUrl` | (local server)           | point at remote viewer (e.g. GitHub Pages)           |
| `-Width`     | 1920                     | viewport width (px)                                  |
| `-Height`    | 1200                     | viewport height (px)                                 |
| `-Scale`     | 2                        | device_scale_factor (1=normal, 2=retina, 3=print)    |
| `-WaitMs`    | 60000                    | per-step timeout (ms)                                |
| `-SettleMs`  | 3000                     | extra wait after layout (ms)                         |
| `-Port`      | 0 (random)               | force a specific local port                          |

## Examples

```powershell
# Subset, fast preview
.\SHOOT.ps1 -Views "V0,V2" -SettleMs 1500

# Higher-res for print / Notion embeds
.\SHOOT.ps1 -Width 2560 -Height 1600 -Scale 2

# Against GitHub Pages instead of local copy
.\SHOOT.ps1 -ViewerUrl "https://soulslike2313.github.io/Imperium-New-Reality/SUPPORT/viewer/"

# Wider settle for slow V1 cose (more nodes)
.\SHOOT.ps1 -Views "V1" -SettleMs 30000 -WaitMs 90000
```

## Output ignored from git

`.\out\*.png` and the directory itself are gitignored (`.gitignore` in this folder).

## When to re-shoot

- After any change to `SUPPORT/viewer/app.js` or `styles.css`.
- After regenerating `SUPPORT/graph_snapshot.json` (different node/edge counts).
- Before sharing a new visual with an external LLM.

## Troubleshooting

- **`playwright not installed`** — run `INSTALL.ps1` first.
- **`Chromium not found`** — `python -m playwright install chromium` separately.
- **Empty/blank PNGs** — increase `-SettleMs` (V1 cose can take 30-40s on a 245-node graph).
- **Port in use** — pass `-Port 8765` to pin a specific one.
- **Remote viewer 404** — your repo isn't published to that URL; use local default.
