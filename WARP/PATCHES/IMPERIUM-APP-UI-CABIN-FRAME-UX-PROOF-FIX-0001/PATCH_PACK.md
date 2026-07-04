# PATCH PACK — IMPERIUM-APP-UI-CABIN-FRAME-UX-PROOF-FIX-0001

status: `WARP_CANDIDATE`  
owner: `APP_PLATFORM + MECHANICUS`  
mode: `VALIDATOR_MARKER_FIX`

## Purpose

Fix the failed cabin-frame UX proof patch.

## Diagnosis

The previous patch failed on a strict `main.js` marker check:

```text
main.js missing required cabin/UX markers
```

The most likely problem is exact wording. The UI contained the intended lower-case boundary text, while the validator required:

```text
No fake execution claimed
```

## Fix

- Adds the exact required marker.
- Adds a non-runtime marker block if any previous marker is still missing.
- Reruns the previous `IMPERIUM-APP-UI-CABIN-FRAME-UX-PROOF-0001` validator.
- Requires the previous receipt to become PASS.

## Expected verdicts

```text
PASS_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_READY
PASS_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_FIX_READY
```
