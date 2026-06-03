# MECHANICUS_PANEL_SLICE_V0_1 (Enhanced to V0_3)

Isolated visual lab slice for:
`SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`

## Current Stage
- Base implementation: V0_1
- Enhancement pass: V0_2 neuro-forge
- Enhancement pass: V0_3 luxury neuro texture pressure
- Mode: static/mock-safe UI with explicit truth boundaries

## Scope
- Root: `IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`
- Stack: plain HTML/CSS/JS only
- No external CDN or framework runtime dependency

## What Was Strengthened in V0_3
1. Shell language moved closer to target reference with richer premium plating and bracketed frame pressure.
2. Visual material depth increased: layered haze, neural lattice, scanline skin, metallic gradients, and pressure chamber treatment.
3. Visible neuro-motion upgraded with a local `requestAnimationFrame` canvas engine:
   - node field synthesis with dynamic links
   - pointer-reactive neural pressure glow
   - pressure chamber bars with live ambient wave
   - subtle parallax shell tilt
4. Header now exposes local motion observability (`FPS (LOCAL)` + motion mode).
5. Tool registry was updated to include installed `node` and `npm`.

## Truth Discipline
- `UNKNOWN`, `STUB`, and `LOCKED` remain explicit.
- No fake `CONNECTED`/`PASS` claims were introduced.
- Neuro motion remains explicitly atmospheric and not backend telemetry.

## State Behavior
`app.js` includes:
- `idle`
- `active`
- `warn`
- `blocked`
- `unknown`

Reduced-motion support:
- `prefers-reduced-motion` fallback
- manual UI toggle `Reduced Motion: ON/OFF`
- motion engine scales down when reduced mode is active

## Evidence
- Screenshots in `SCREENSHOTS/` (including `01_full.png` and `02_detail_*.png`)
- Reports in `REPORTS/`
- V0_3 receipt in `RECEIPTS/FINAL_RECEIPT_V0_3.json`

## Open Locally
Open `index.html` in browser (no build step required).
