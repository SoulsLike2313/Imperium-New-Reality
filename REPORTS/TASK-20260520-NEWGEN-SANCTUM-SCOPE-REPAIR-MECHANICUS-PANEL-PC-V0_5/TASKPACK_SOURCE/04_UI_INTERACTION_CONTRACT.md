# UI Interaction Contract

## Required mental model

Sanctum is becoming the shell of the IMPERIUM brain.

- Organs are peripheral brain zones.
- The center is neural communication.
- Clicking a real organ must open its working panel.
- Mechanicus is currently the only real active organ.
- Placeholder organs may show placeholder cards only.
- Custodes and Throne remain locked.

## Mechanicus interaction

User action:
1. Open Sanctum.
2. See brain overview.
3. Click `Mechanicus` node.

Expected result:
- Mechanicus node becomes selected.
- A Mechanicus operator panel opens.
- The panel is not just a log dump.
- The panel has command controls and live state.
- Owner can run allowed commands from the panel.

BLOCK if:
- click does nothing;
- selection is invisible;
- panel does not open;
- operator panel is only raw terminal output;
- command controls are missing or non-functional.

## Panel sections

Required sections:
- Header / top status strip
- Mission / identity strip
- Work zone / current activity
- Command zone / operator palette
- Tool registry / capability overview
- Latest report / latest receipt
- Event summary
- SSE/live transport status
- RAW/technical mode

## Responsive behavior

At 1366x768:
- header must fit;
- command zone must be visible;
- work zone must be visible;
- main body must not require horizontal page scroll;
- raw logs must not consume the whole viewport.

At 1920x1080:
- panel may expand into more cinematic layout.

## Truth labels

The panel must visually distinguish:
- REAL
- PLACEHOLDER
- LOCKED
- UNKNOWN
- UNPROVEN
- FALLBACK
- PASS/WARN/BLOCK
