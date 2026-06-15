# Reference Interpretation Card

Reference image:

- `REFERENCES/target_mechanicus_console_reference.png`

Negative examples:

- `REFERENCES/NEGATIVE_EXAMPLES/current_live_bad_example_01.png`
- `REFERENCES/NEGATIVE_EXAMPLES/current_live_bad_example_02.png`
- `REFERENCES/NEGATIVE_EXAMPLES/current_bundle_answer_example.png`

## Extracted intent

1. The screen must read as an operator console, not a plain log stream.
2. Truth/status needs a dedicated top strip with high contrast and compact chips.
3. Work context and command access should have clear, separate zones.
4. Tool/capability summary should be quick to scan and semantically colored.
5. Technical raw output must be present but subordinate.

## Anti-patterns to avoid

1. Raw terminal taking the largest or most dominant area by default.
2. Flat generic cards with little hierarchy or grouping.
3. Typography too small for 1366x768.
4. Decorative motion that competes with operator reading flow.

## Implementation mapping

1. Top truth strip with mission text and status chips.
2. Left work zone for timeline/events.
3. Right command rail with action tiles and raw-mode toggle.
4. Center tool registry and event summaries.
5. Hidden-by-default raw pane, revealed on explicit command.

