# IMPERIUM TUI WINDOWED AQUARIUM LAUNCHER REPORT V0.1 SELFTEST JSON HOTFIX

task_id: `IMPERIUM-TUI-WINDOWED-AQUARIUM-SELFTEST-JSON-HOTFIX-0001`  
validator_id: `imperium_tui_windowed_aquarium_selftest_json_hotfix.v0_1`  
verdict: `PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_READY`  
generated_at_utc: `2026-07-02T11:58:22Z`

## Meaning

The validator now parses self-test JSON from noisy PowerShell stdout.

This fixes the false failure where the windowed launcher self-test passed, but the validator could not parse `action_count` because shell profile text preceded the JSON.

## Run

```powershell
pwsh SUPPORT/TUI/imperium_tui_window.ps1
```

## Checks

- `PASS` — imperium_tui_window.ps1_exists
- `PASS` — IMPERIUM_TUI_ACTIONS_V0_1.json_exists
- `PASS` — IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_MATRIX_V0_1.json_exists
- `PASS` — README_IMPERIUM_TUI_WINDOWED_AQUARIUM_V0_1.md_exists
- `PASS` — windowed_aquarium_matrix_parses
- `PASS` — actions_manifest_available
- `PASS` — windowed_launcher_has_required_ui_markers
- `PASS` — windowed_launcher_does_not_execute_git
- `PASS` — windowed_launcher_selftest_passes
- `PASS` — selftest_reports_action_count_or_manifest_confirms

## Warnings

- none

## Errors

- none
