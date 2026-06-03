# Manual Open Instructions

## Direct local open

1. Open file:
   `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_VISUAL_FOUNDRY\LAB\index.html`

2. First checks:
   - brain field dominates left/center area (large pulsing core + neural halos)
   - split-screen layout is active (brain dominion left, cockpit panel right)
   - right panel updates when clicking organ zones
   - raw mode stays hidden until `RAW OFF/RAW ON` toggle

3. Optional language check:
   - click `EN/RU` toggle in top-right corner

## Screenshot regeneration

1. `cd E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_VISUAL_FOUNDRY\PLAYWRIGHT`
2. `npm install`
3. `npm run screenshots`
4. `python validate_artifacts.py`

Outputs:

- screenshots: `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_VISUAL_FOUNDRY\SCREENSHOTS`
- validation: `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_VISUAL_FOUNDRY\REPORTS\validation_report.json`
