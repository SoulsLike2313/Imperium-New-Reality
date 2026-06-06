# ORGAN TUI STANDARD V0.1

## Mandatory Runtime

- Renderer: `Rich` is mandatory primary path.
- Fallback plain text is allowed only for diagnostics; do not claim full visual pass from plain fallback.

## Mandatory CLI Flags

- `--smoke`: render non-interactive proof screen and exit `0` on success.
- `--plain-json`: emit machine-readable summary/verdict payload.
- `--task-id <TASK_ID>`: allow task binding.

## Mandatory Screen Blocks

1. Organ identity/responsibility.
2. Active contracts and gate highlights.
3. Current state summary.
4. Servitor ask-map (what must be asked).
5. Warn/block profile.
6. Evidence paths/requirements.

## Color Direction (Wave 1)

- `DOCTRINARIUM`: gold + bordeaux/parchment.
- `OFFICIO_AGENTIS`: steel blue + cyan.
- `MECHANICUS`: red + amber/copper.
- `ADMINISTRATUM`: green + bronze/parchment gray.

## Non-Blocking Rule

Smoke mode must never wait for interactive input and must not run endless loop.

## PASS Criteria (TUI Slice)

- script launches;
- Rich render path works;
- smoke exits `0`;
- plain JSON output is parseable;
- screen includes all mandatory blocks.
