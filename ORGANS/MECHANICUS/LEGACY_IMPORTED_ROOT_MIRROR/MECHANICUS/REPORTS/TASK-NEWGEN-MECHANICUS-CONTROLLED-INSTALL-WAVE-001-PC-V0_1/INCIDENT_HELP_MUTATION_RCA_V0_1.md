# Incident RCA — help-triggered mutation

- Incident ID: INCIDENT-MECH-RUNNER-HELP-MUTATION-20260526
- Trigger command: `python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py --help`
- Expected behavior: read-only introspection
- Observed behavior: full execution path with tracked file writes

## Why it happened
- `mechanicus_controlled_provision_runner_v0_1.py` has **no argparse-based introspection mode**.
- Entry point `if __name__ == "__main__": raise SystemExit(main())` always runs `main()`.
- `main()` immediately initializes write paths and performs report/receipt/registry mutations.
- No import-time write side effects were found in imported receipt builders; mutation came from runtime execution path of `main()`.

## Exact mutator source
- File: `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py`
- Function: `main()` (line ~495)
- First write-capable init: `report_root.mkdir(...)` (line ~499)
- Subsequent writers: `write_json`, `write_text`, `rebuild_registry`, scope exporter, fake-canon detector calls.

## Changed files
- Count: 24
- Full list captured in `raw/incident/incident_git_diff_name_status_before_cleanup.txt` and JSON payload.

## Prevention contract (mandatory)
- `--help`, `--version`, `--list`, `--show-config` must be read-only.
- Parse args before any write-capable initialization.
- No script writes on import.
- Default mode read-only; writes only with explicit execution flag.
- Declare output paths before any write operation.
- Keep report writing behind explicit execution path only.
- Add smoke gate: compare `git status --short` before/after introspection command and fail on drift.

## Immediate containment for this task
- Dirty incident evidence saved.
- Out-of-task mutations will be restored to `HEAD`.
- Clean state proof required before Wave 001 continuation.

## Recommended follow-up task
- `TASK-NEWGEN-MECHANICUS-RUNNER-READONLY-INTROSPECTION-HARDENING-PC-V0_1`
- Scope: read-only introspection contract, no import-time writes, explicit write mode, smoke test across Mechanicus runner family, hard fail on repo mutation under read-only commands.
