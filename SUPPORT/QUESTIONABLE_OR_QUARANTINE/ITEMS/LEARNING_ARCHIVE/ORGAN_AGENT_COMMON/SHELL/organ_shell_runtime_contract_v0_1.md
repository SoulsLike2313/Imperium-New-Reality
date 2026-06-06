# ORGAN SHELL Runtime Contract V0.1

## Runtime Component

`IMPERIUM_NEW_GENERATION/ORGAN_AGENT_COMMON/SHELL/organ_shell_v0_1.py`

## Security Boundary

- Input command line is parsed into allowlisted command keys only.
- No path from user command text is executed as OS shell command.
- Unknown commands return `BLOCK`.
- All built-in handlers are read-only and bounded.

## Required Modes

- interactive (default);
- `--smoke`;
- `--scripted-test`;
- `--command <allowlisted_command>`;
- optional `--plain-json`.

## Rendering

When Rich is available, render shell zones:

- identity header;
- status bar;
- work/activity zone;
- command palette;
- mission/focus;
- evidence/latest report zone;
- bottom event strip.

When Rich is not available:

- return `BLOCK` exit code and explicit machine-readable evidence;
- do not silently downgrade to fake visual PASS.

## Command Contract

Base command family:

- `status`
- `identity`
- `gates`
- `query`
- `evidence`
- `help`
- `clear`
- `exit`

Organ-specific families are injected by launcher config and remain allowlisted.

## Smoke / Scripted Proof Contract

- `--smoke` must run bounded allowlisted sequence and print proof marker.
- `--scripted-test` must run bounded allowlisted sequence and print proof marker.
- Both modes must exit without interactive wait.

## Exit Codes

- `0`: success / bounded warn that does not block shell claim.
- `2`: command-level block (unknown command or blocked handler result).
- `3`: renderer block (Rich unavailable) or runtime precondition failure.
