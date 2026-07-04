# PATCH PACK — IMPERIUM-APP-UI-RIGHT-RAIL-COMMAND-DECK-V3-FIX-0001

status: `WARP_CANDIDATE`  
owner: `APP_PLATFORM + MECHANICUS`  
mode: `VALIDATOR_SIZE_GATE_FIX`

## Purpose

Fix the failed v3 command deck patch.

## Diagnosis

The previous v3 validator failed only on:

```text
styles.css too small for command deck v3
```

## Fix

Append a real, semantic CSS extension:

- hero edge rail;
- command rail internal ornaments;
- room icon material variants;
- status tile telemetry sweep;
- card glow variants;
- table registry watermark;
- focus-visible affordances.

Then rerun the previous v3 validator and require the previous v3 receipt to become PASS.

## Expected verdicts

```text
PASS_IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3_READY
PASS_IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3_FIX_READY
```
