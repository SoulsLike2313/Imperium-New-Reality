# Performance Truth Report

## Measurement Method
- Tool: Playwright headless chromium probe (`performance_probe.mjs`)
- Sample: 180 `requestAnimationFrame` frames
- Environment: local PC, headless browser context

## Results
- Approx FPS: `44.92`
- Avg frame time: `22.261 ms`
- P95 frame time: `16.8 ms`

## Interpretation
- UI animation is smooth enough for operator workflow in local usage.
- Hard 60fps verification is not claimed from this headless run.
- Additional headed/profiled sampling is recommended before claiming strict 60fps conformance.

## Evidence
- `PERFORMANCE_PROBE.json`
- `POST_PLAYWRIGHT/screenshots/01_overview.png`
- `POST_PLAYWRIGHT/screenshots/02_active_brain_or_organ_zone.png`
