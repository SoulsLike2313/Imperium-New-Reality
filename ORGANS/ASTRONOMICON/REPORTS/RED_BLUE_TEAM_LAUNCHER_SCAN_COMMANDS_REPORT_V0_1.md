# RED + BLUE TEAM LAUNCHER SCAN COMMANDS REPORT V0.1

task_id: `RED-BLUE-TEAM-LAUNCHER-SCAN-COMMANDS-0001`  
validator_id: `red_blue_team_launcher_scan_commands_validator.v0_1`  
verdict: `PASS_RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_READY`  
generated_at_utc: `2026-07-02T10:38:49Z`  
repo_head: `893347e8a578b861f59b978c60d55e6ab2319716`

## Commands

```text
imperium redblue scan
imperium redblue scan organ <ORGAN>
imperium redblue summary
imperium organ <ORGAN> redblue
```

## Meaning

The operator can now view Red/Blue skill lane status from the launcher.

The command shows definition readiness and proof gap. It does not prove Red/Blue.

## Not claimed

- red_team_proven
- blue_team_proven
- Custodes trust
- Throne verdict
- organ assembled

## Checks

- `PASS` — imperium_cli.py_exists
- `PASS` — LAUNCHER_COMMANDS_V0_4.json_exists
- `PASS` — RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_MATRIX_V0_1.json_exists
- `PASS` — red_blue_team_skills_scan.py_exists
- `PASS` — launcher_v0_4_commands_parse
- `PASS` — redblue_launcher_commands_declared
- `PASS` — redblue_launcher_matrix_parses
- `PASS` — launcher_redblue_scan_runs
- `PASS` — launcher_redblue_scan_organ_inquisition_runs
- `PASS` — launcher_redblue_summary_runs
- `PASS` — launcher_organ_inquisition_redblue_runs
- `PASS` — launcher_redblue_prove_forbidden
- `PASS` — launcher_redblue_attack_forbidden
- `PASS` — launcher_redblue_defend_forbidden
- `PASS` — redblue_scan_summary_still_defined_not_proven

## Warnings

- none

## Errors

- none
