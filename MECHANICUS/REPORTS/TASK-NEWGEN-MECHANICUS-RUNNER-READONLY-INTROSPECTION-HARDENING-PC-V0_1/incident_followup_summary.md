# Incident Follow-up Summary — TASK-NEWGEN-MECHANICUS-RUNNER-READONLY-INTROSPECTION-HARDENING-PC-V0_1

## Incident lineage

- Wave001 incident proved `mechanicus_controlled_provision_runner_v0_1.py --help` executed `main()` and wrote artifacts.
- Wave001 side effect note identified three checker scripts that overwrote historical reports by default.

## Hardening delivered

1. Runner hardening (`mechanicus_controlled_provision_runner_v0_1.py`):
- Added argparse read-only introspection surface (`--help`, `--version`, `--list`, `--show-config`).
- Added explicit write gate `--execute`; without it runner returns read-only message and exits.
- Preserved original mutating flow under `run_mutating_execution(...)`.
- Updated scope-export input path derivation to use resolved report root.

2. Checker hardening:
- `check_owner_approved_tool_normalization_v0_1.py`
- `check_mechanicus_owner_approval_matrix_v0_1.py`
- `check_mechanicus_arsenal_foundation_v0_1.py`

For all three checkers:
- Added `--version`, `--list`, `--show-config` introspection flags.
- Added explicit write controls: `--write-report` and `--report-output`.
- Default behavior is now read-only: checker runs and prints summary JSON but does not write report files unless write mode is explicit.

## Evidence highlights

- Read-only smoke: 24/24 PASS (`read_only_smoke_results.json`).
- Every tested read-only command preserved identical `git status --short` hash before/after.
- Import smoke for all 4 modules passed with no repo mutations.
- Explicit write-mode smoke wrote checker outputs only into current task report folder.

## Historical report protection outcome

- Historical report overwrite-by-default behavior is removed for the three identified checkers.
- Writing reports now requires explicit operator intent and path.

