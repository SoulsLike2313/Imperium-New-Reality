# CODEX UI OUTSOURCE CODE REVIEW V0.1

source_pack: `codex_ui_reference_outsource_review_pack.zip`  
reviewed_by: `LOGOS_PRIME`  
status: `EXTERNAL_CODE_REVIEW_NOT_CANON`

## Measured surface

The uploaded Codex review pack contained:

| File | Size / shape |
|---|---:|
| `main.js` | 812 lines / 36.8 KB / 40 functions / 87 `const` declarations / 17 mutable `let` globals |
| `styles.css` | 3368 lines / 68.5 KB / ~498 selector blocks / 10 media blocks / 5 keyframes |
| `main.rs` | 312 lines / 12.0 KB |
| `OUTSOURCE_REPORT.md` | 174 lines |

Largest frontend functions detected:

| Function | Lines |
|---|---:|
| `render` | 102 |
| `renderCommandRail` | 49 |
| `startFpsWatchdog` | 45 |
| `renderPatchForge` | 36 |
| `renderOrganHub` | 34 |

## Diagnosis

Codex produced a useful external candidate, but the implementation confirms the deeper development problem:

```text
The UI is still a monolith.
```

`main.js` mixes:

- global state;
- room data models;
- patch registry command bridge;
- Aquarium log state;
- heartbeat/FPS telemetry;
- resizing/layout state;
- all room renderers;
- all component renderers;
- event binding;
- runtime FPS proof.

`styles.css` mixes:

- tokens;
- global reset;
- layout;
- room navigation;
- command rail;
- organ cards;
- Aquarium;
- buttons;
- table styling;
- ornament;
- animation;
- responsive behavior;
- reference-fidelity bitmap mode.

`main.rs` is not disastrous yet, but it already mixes:

- repo discovery;
- app copy discovery;
- patch registry;
- path safety;
- process execution;
- receipt writing;
- runtime FPS proof;
- log/open commands.

## Critical finding: reference bitmap mode

The Codex CSS contains a reference-fidelity mode:

```css
/* REFERENCE_FIDELITY_BITMAP_SKIN_0001
   Explicit proof mode: ?refFidelity=1.
   Uses the supplied reference image as a full-size art chassis while keeping live DOM controls as hit zones. */

.app-shell.reference-fidelity::before {
  background: url("./assets/reference-target-full.png") center / 100% 100% no-repeat !important;
}

.reference-fidelity .hero,
.reference-fidelity .room-nav,
.reference-fidelity .main-deck,
.reference-fidelity .command-rail,
.reference-fidelity .aquarium {
  opacity: 0 !important;
}
```

This is useful as a visual reference aid, but it must never be counted as live UI fidelity proof. It is a controlled illusion: a full reference bitmap with hidden DOM hit zones.

## Why this explains slow UI progress

We were patching visual output without first building a visual production system.

That creates exhaustion because Owner must manually validate everything each time:

- Is it closer?
- Is it fake?
- What did it break?
- What is duplicated?
- What is readable?
- What is only a screenshot illusion?
- Which pieces are reusable?

The current form has no stable seams. Any UI improvement tends to touch one giant JS file and one giant CSS file. This makes every patch high-cognitive-load and high-regression-risk.

## What is worth salvaging

- heartbeat/cardiogram telemetry idea;
- Operational Law block;
- metadata deduplication rules;
- Aquarium as Proof Console;
- slightly larger typography;
- nav medallion direction;
- evidence/reporting discipline.

## What must not be salvaged as-is

- giant `main.js`;
- giant `styles.css`;
- full reference bitmap as fidelity proof;
- invisible live DOM over image chassis;
- goal-mode claim that visual target is reached;
- marker validators that pass a monolith.

## Required next architectural step

Create Mechanicus UI Workshop foundation:

```text
tokens -> components -> rooms -> services -> assets -> evidence -> Owner acceptance
```

Then port visual improvements into that structure. Do not continue stacking CSS on the monolith.
