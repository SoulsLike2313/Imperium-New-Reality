# ORGAN_SHELL_V1

Task scope: `TASK-20260524-NEWGEN-IMPORTANT-SIX-ORGAN-SHELL-V1-PC-V0_1`

## Purpose

`ORGAN_SHELL_V1` is a shared Rich-based interactive-lite shell contract for Important Six organs.

It upgrades organ TUI behavior from snapshot-only rendering to a personal shell model:

- command prompt loop (interactive mode);
- allowlisted command execution only;
- visible work zone, command zone, mission zone, evidence zone, and status strip;
- smoke/scripted/one-command non-interactive modes for safe proof.

## Required Launch Modes

- Interactive:
  - `python .../<organ>_shell_v0_1.py`
- Smoke:
  - `python .../<organ>_shell_v0_1.py --smoke`
- Scripted test:
  - `python .../<organ>_shell_v0_1.py --scripted-test`
- One command:
  - `python .../<organ>_shell_v0_1.py --command status`

Optional:
- `--plain-json` for machine-readable snapshots.

## Safety Model

- No arbitrary shell command execution.
- No write/destructive actions exposed through shell commands.
- Commands are strict allowlist and mapped to bounded read-only handlers.
- Unknown commands return `BLOCK` result and remain inside shell.

## Base Command Set

Every organ shell includes:

- `status`
- `identity`
- `gates`
- `query`
- `evidence`
- `help`
- `clear`
- `exit`

## Organ-Specific Commands

- Doctrinarium: `laws`, `preflight`
- Officio Agentis: `role`, `language`
- Administratum: `continuity`, `receipts`
- Astronomicon: `route`, `stages`
- Mechanicus: `tools`, `capability`
- Inquisition: `audit`, `fakegreen`

## Visual Zones

`ORGAN_SHELL_V1` renders all zones in one shell frame:

- identity header;
- top status bar;
- work/activity zone;
- command palette zone;
- mission/focus zone;
- evidence/latest-report zone;
- bottom event/status strip;
- prompt line in interactive mode.

## Claim Boundary

Proven by this slice:

- personal shell UX for Important Six in terminal context;
- bounded allowlisted command model;
- smoke/scripted/command execution proof.

Not proven:

- browser embedded PTY;
- production orchestration;
- Owner verdict control surface;
- final AAA visual lock.
