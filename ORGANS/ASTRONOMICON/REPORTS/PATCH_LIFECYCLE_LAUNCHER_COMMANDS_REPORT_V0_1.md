# PATCH LIFECYCLE LAUNCHER COMMANDS REPORT V0.1

task_id: `PATCH-PACK-LIFECYCLE-LAUNCHER-COMMANDS-0001`  
validator_id: `patch_lifecycle_launcher_commands_validator.v0_1`  
verdict: `PASS_PATCH_LIFECYCLE_LAUNCHER_COMMANDS_READY`  
generated_at_utc: `2026-07-01T20:08:32Z`  
repo_head: `91b1cc7ec902eb7ae8b319d02d4a97742f026a36`

## Commands now available

```text
imperium patch preflight <PATCH_ID>
imperium patch scope <PATCH_ID>
imperium patch smoke <PATCH_ID>
imperium patch smoke-all
imperium patch smoke-summary
imperium patch smoke-partial
imperium patch smoke-closed
imperium patch lifecycle <PATCH_ID>
imperium patch lifecycle-all
```

## Not claimed

- patch execution
- Custodes trust
- Throne verdict

## Checks

- `PASS` — imperium_cli.py_exists
- `PASS` — imperium.ps1_exists
- `PASS` — LAUNCHER_COMMANDS_V0_2.json_exists
- `PASS` — PATCH_LIFECYCLE_LAUNCHER_COMMANDS_MATRIX_V0_1.json_exists
- `PASS` — LAUNCHER_COMMANDS_V0_2.json_parses
- `PASS` — PATCH_LIFECYCLE_LAUNCHER_COMMANDS_MATRIX_V0_1.json_parses
- `PASS` — launcher_does_not_implement_git_commit_push
- `PASS` — launcher_lifecycle_commands_declared
- `PASS` — launcher_patch_preflight_command_runs
- `PASS` — launcher_patch_scope_command_runs
- `PASS` — launcher_patch_smoke_command_runs
- `PASS` — launcher_patch_lifecycle_command_runs
- `PASS` — launcher_patch_run_is_forbidden
- `PASS` — operator_lifecycle_receipt_written

## Warnings

- none

## Errors

- none
