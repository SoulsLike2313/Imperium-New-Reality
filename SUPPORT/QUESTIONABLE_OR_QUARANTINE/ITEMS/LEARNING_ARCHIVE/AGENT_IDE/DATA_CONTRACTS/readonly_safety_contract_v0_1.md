# Read-only Safety Contract V0.1

Agent IDE V0.1 is read-only.

## Forbidden capabilities

- File write/edit/save operations.
- Shell or command execution.
- Git commit/push/reset actions.
- Delete/move/quarantine actions.
- WARP or CLI worker runtime actions.
- Dynamic execution of plugin code.

## Allowed capabilities

- Read JSON/JSONL and render UI.
- Filter/search/sort in-memory data.
- Display warnings and missing-source states.
- Copy text/path to clipboard.
- Reload data from disk.

## Verification expectations

- Source scan confirms no `subprocess`, `os.system`, or write-open mode.
- Smoke test confirms data load and view model build.
- Scope checker confirms only task scope paths are changed.
