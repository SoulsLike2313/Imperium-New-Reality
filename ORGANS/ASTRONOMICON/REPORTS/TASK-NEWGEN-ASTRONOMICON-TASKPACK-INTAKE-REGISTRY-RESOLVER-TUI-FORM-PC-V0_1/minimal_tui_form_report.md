# Minimal TUI Form Report

The minimal text UI is available at:
`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TOOLS/astronomicon_task_entry_tui_v0_1.py`

Executed commands:
- `--show-current` -> `tui_show_current.txt`
- `--resolve-current` -> `tui_resolve_current.txt`
- `--register-zip <existing task>` (duplicate test) -> `tui_register_duplicate_attempt.txt`

Observed behavior:
- shows current expected task payload;
- resolves current task_id and prints owner next instruction;
- duplicate registration is blocked with `CAP_DUPLICATE_TASK_ID_NOT_DETECTED`.
