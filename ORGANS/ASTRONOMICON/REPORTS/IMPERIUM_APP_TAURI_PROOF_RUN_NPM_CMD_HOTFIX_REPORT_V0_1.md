# IMPERIUM APP TAURI PROOF RUN NPM CMD HOTFIX REPORT V0.1

task_id: `IMPERIUM-APP-TAURI-PROOF-RUN-NPM-CMD-HOTFIX-0001`  
validator_id: `imperium_app_tauri_proof_run_npm_cmd_hotfix_validator.v0_1`  
verdict: `FAIL_IMPERIUM_APP_TAURI_PROOF_RUN_NPM_CMD_HOTFIX`  
generated_at_utc: `2026-07-02T14:21:58Z`

## Meaning

The first proof-run failed on:

```text
command failed: npm --version
```

On Windows, npm is commonly resolved through `npm.cmd`. This hotfix makes the proof-run validator execute npm commands through:

```text
cmd.exe /d /s /c npm ...
```

Then it reruns the proof-run.

## Checks

- `PASS` — proof_validator_is_windows_npm_cmd_aware
- `FAIL` — proof_run_passes_with_windows_npm_cmd_execution
- `FAIL` — proof_receipt_is_pass_after_hotfix

## Warnings

- none

## Errors

- proof run still does not pass with Windows npm/cmd execution
