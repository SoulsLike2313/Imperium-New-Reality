# IMPERIUM APP TAURI RUNTIME FPS CONTRACT NAME HOTFIX REPORT V0.1

task_id: `IMPERIUM-APP-TAURI-RUNTIME-FPS-CONTRACT-NAME-HOTFIX-0001`  
validator_id: `imperium_app_tauri_runtime_fps_contract_name_hotfix_validator.v0_1`  
verdict: `PASS_IMPERIUM_APP_TAURI_RUNTIME_FPS_CONTRACT_NAME_HOTFIX_READY`  
generated_at_utc: `2026-07-02T14:50:50Z`

## Meaning

The runtime FPS patch failed before opening Tauri because a required file was missing.

Root cause:

```text
validator expected:
SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_WINDOW_FPS_PROOF_CONTRACT_V0_1.json

previous patch wrote:
SUPPORT/APP_TAURI/contracts/IMPERIUM_TAURI_RUNTIME_FPS_PROOF_CONTRACT_V0_1.json
```

This hotfix adds the canonical expected filename and reruns the runtime window FPS validator.

## Checks

- `PASS` — expected_runtime_window_fps_contract_exists_and_parses
- `PASS` — old_short_contract_name_may_exist_but_is_not_required
- `PASS` — runtime_window_fps_validator_rerun_after_contract_name_fix
- `PASS` — runtime_window_fps_receipt_is_pass_after_contract_name_fix

## Warnings

- old short contract filename still exists; harmless, but canonical validator requires the WINDOW filename

## Errors

- none
