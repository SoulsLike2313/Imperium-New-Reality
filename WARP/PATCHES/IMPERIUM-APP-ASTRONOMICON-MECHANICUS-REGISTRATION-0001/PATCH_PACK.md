# IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001

## Purpose
Move Patch Pack registration into the Astronomicon room of the Tauri app and make registration call Mechanicus for a script-first organ summary.

## Scope
- Tauri frontend: Astronomicon registration room, compact Mechanicus summary cards, Patch Forge demoted to execution staging.
- Tauri backend: `register_patch_pack_with_organs` and `analyze_patch_pack_organ_summary` commands.
- Mechanicus: app patch pack analysis matrix.
- Astronomicon: app registration law/matrix and next hard trial candidate for Eyes/Canvas.

## No fake-green boundaries
- No real execution is enabled.
- This is product integration proof, not full Core v1.
- Full JSON stays in report files; terminal output is compact by default.

## Expected verdict
`PASS_IMPERIUM_APP_ASTRONOMICON_MECHANICUS_REGISTRATION_READY`


## Hotfix note

Validator resolves Windows command shims such as `npm.cmd` before host build checks. Terminal output remains compact; full JSON is opt-in via `-VerboseJson`.
