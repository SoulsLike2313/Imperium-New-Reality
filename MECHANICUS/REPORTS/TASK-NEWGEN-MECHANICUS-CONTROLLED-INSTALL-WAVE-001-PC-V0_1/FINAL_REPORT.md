# FINAL REPORT

## Task
TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1

## Incident engineering answer (required)
1. Why this happened:
- `mechanicus_controlled_provision_runner_v0_1.py --help` mutated the repo because the script has no argparse read-only help path.
- Report/receipt/registry writes are in `main()` and `__main__` always executes `main()`.
- No import-time file writes were observed in imported receipt builders; mutation source is runtime execution path.
- Exact mutator source: `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py`, function `main()` (~line 495), with first write-capable init `report_root.mkdir(...)` (~line 499).
- Changed files are captured in `raw/incident/incident_git_diff_name_status_before_cleanup.txt`.
2. Prevention rules:
- Introspection commands (`--help`, `--version`, `--list`, `--show-config`) must be hard read-only.
- Argument parsing must complete before any write-capable initialization.
- No import-time writes in scripts.
- Default mode read-only; explicit execution flag required for writes.
- Scripts must declare output paths before writing.
- Report/registry writes only behind explicit execution branch.
- Add smoke gate: run read-only command and fail if `git status --short` changes.
3. Immediate containment performed:
- Dirty-state evidence saved.
- Unintended out-of-task changes restored to HEAD.
- Clean containment proof recorded before Wave 001 execution.
4. Follow-up hardening task:
- Proposed task: `TASK-NEWGEN-MECHANICUS-RUNNER-READONLY-INTROSPECTION-HARDENING-PC-V0_1`.
- Scope: read-only introspection contract, no import-time writes, clean-state smoke test for all Mechanicus runners, mutation allowed only in explicit execution mode, fail if read-only commands mutate repo.
- Additional checker hardening lesson: checker scripts must not overwrite historical accepted task report folders by default; checker output must go to current task report folder or explicit output path.

## Wave 001 summary
- Prerequisites ready: winget=True, npm=True, pip=True, python=True
- Prerequisite installs/repairs: none required (only path repair for Python user Scripts to expose CLI binaries).
- 7-Zip: existing official local executable validated by fixtures.
- markdownlint-cli/check-jsonschema/yamllint: installed or repaired via approved routes and validated by pass/fail fixtures.
- Capability cards updated to SANDBOX; no CANON claims.

## Evidence index
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/prerequisite_install_receipts.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/tool_install_receipts.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/validation_receipts.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/stability_matrix.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/registry_update_report.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/checker_run_report.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/external_tool_introduction_matrix.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/ghost_evolve_sidecar.json
- IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/closure_receipt.json

## Interim verdict
PASS

## Next allowed task recommendation
TASK-NEWGEN-MECHANICUS-RUNNER-READONLY-INTROSPECTION-HARDENING-PC-V0_1

## Commit/Push Status
- commit: cf6192a07fc8347f1948a5ba57dfcbd8b4aa7557
- remote: origin/master
- remote_sync: yes
- worktree_clean_after_push: pending_final_receipt_commit
