# Performance Truth Report

## Method
- Playwright + `requestAnimationFrame` sample probe (`performance_probe.mjs`)
- sample size: 180 frames
- target url: `http://127.0.0.1:8877`

## Measured Results
- approx_fps: `39.34`
- avg_frame_ms: `25.42`
- p95_frame_ms: `16.9`

## Truth Interpretation
- No claim of strict 60 FPS is made.
- Visual quality improved while preserving truth readability.
- Additional performance optimization is still possible and recommended for future pass.

## Evidence
- `PERFORMANCE_PROBE.json`
- `POST_PLAYWRIGHT/screenshots/01_overview.png`
