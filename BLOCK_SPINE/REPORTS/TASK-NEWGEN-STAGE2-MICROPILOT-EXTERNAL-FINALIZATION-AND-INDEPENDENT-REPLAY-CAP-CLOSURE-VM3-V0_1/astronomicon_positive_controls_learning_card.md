# Astronomicon Positive Controls Learning Card

Task: TASK-NEWGEN-STAGE2-MICROPILOT-EXTERNAL-FINALIZATION-AND-INDEPENDENT-REPLAY-CAP-CLOSURE-VM3-V0_1
Generated at: 2026-06-01T11:47:57Z

## What was preserved
- Missing MANIFEST, missing language policy, missing 8-organ route, and unregistered TASK_ID were preserved as intentional protection fixtures.
- Valid 8-organ taskpack flow was preserved as positive control (admission PASS + resolver PASS_WITH_WARNINGS).

## Why this matters
- Builders now have a concrete admission contract to satisfy before Owner launch.
- Resolver safety is treated as a capability, not friction.

## Next builder actions
- Always include root MANIFEST.json.
- Always include complete language_and_encoding_policy.
- Always provide all 8 organs in MANIFEST.organs.
- Register TASK_ID before issuing Owner launch phrase.
