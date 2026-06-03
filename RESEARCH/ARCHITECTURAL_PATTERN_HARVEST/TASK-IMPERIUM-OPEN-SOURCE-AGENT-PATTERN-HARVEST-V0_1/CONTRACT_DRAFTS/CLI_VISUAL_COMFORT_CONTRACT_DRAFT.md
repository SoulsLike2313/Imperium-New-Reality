# CLI Visual Comfort Contract Draft

## Purpose

Make local agent work pleasant and readable without turning CLI beauty into fake proof.

## Modes

```text
--pretty
--compact
--plain-json
--no-color
--verbose
```

## Visual layout

Every pretty command should render:

```text
[ADMINISTRATUM_AGENT]
RUN: RUN-...
STATUS: CHECKING / PASS / WARN / FAIL / STOP
SCOPE: ...

[1] Input
[2] Checks
[3] Actions
[4] Outputs
[5] Receipts
[6] Warnings
[7] Next action
```

## Rules

- Green is only for verified PASS.
- Yellow is warning/pending.
- Red is fail/blocked.
- Blue/cyan is info.
- Pretty output never replaces JSON reports.
- No giant white-wall text by default.
- Tables should be compact and aligned.
- Use ASCII-safe fallback when Unicode/ANSI fails.
- Future Rich/Textual rendering is allowed only after separate tool verification.
