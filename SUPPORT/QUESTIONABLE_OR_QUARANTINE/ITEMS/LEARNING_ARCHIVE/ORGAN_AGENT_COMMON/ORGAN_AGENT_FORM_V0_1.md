# ORGAN AGENT FORM V0.1 (Wave 1 Foundation)

## Purpose

This form defines the minimum usable structure for an IMPERIUM NewGen organ-agent.
It is optimized for Servitor execution discipline, machine-readable verdicts, and launchable terminal UX.

## Required Blocks

1. `IDENTITY`
2. `CONTRACTS`
3. `GATES`
4. `TOOLS`
5. `TUI`
6. `STATE`
7. `TEMPLATES`
8. `REPORTS`

## Required Files Per Organ

- `IDENTITY/organ_identity_v0_1.md`
- `CONTRACTS/servitor_contract_v0_1.md`
- `GATES/organ_gate_catalog_v0_1.json`
- `TEMPLATES/organ_verdict_template_v0_1.json`
- `STATE/current_state_v0_1.json`
- `TOOLS/<organ_slug>_organ_query_v0_1.py`
- `TUI/<organ_slug>_tui_v0_1.py`

## Identity Rules

Identity must explicitly state:
- organ id and slug;
- responsibility slice;
- what Servitor must ask this organ first;
- what this organ can `PASS / WARN / BLOCK / OWNER_VERDICT_NEEDED`.

## Contract Rules

Servitor contract must include:
- accepted input shape;
- required evidence;
- forbidden actions;
- stop conditions;
- not-proven boundary.

## Gate Rules

Each organ gate catalog must expose:
- gate id;
- severity;
- pass condition;
- block condition;
- evidence requirement.

## Tool Rules

Organ query tool must:
- return machine-readable verdict payload;
- include applied rules and required actions;
- support sample/smoke response mode.

## TUI Rules

Organ TUI must:
- use Rich as primary renderer;
- support `--smoke`;
- support `--plain-json`;
- show identity, responsibility, gates/contracts/state, ask/warn/block map, evidence refs;
- exit without waiting for interactive input in smoke mode.

## Owner Verdict Needed Protocol

If an organ cannot safely continue in bounded scope, it must emit:
- `verdict=OWNER_VERDICT_NEEDED`;
- clear owner question (Russian text field for owner use);
- allowed answers (`approve|reject|revise_scope|pause`);
- explicit blocked status until owner answer.

## Smoke Requirements

Minimum smoke pack:
1. launch all four Wave 1 TUIs with `--smoke`;
2. run all four organ query tools in sample mode;
3. validate generated/required JSON artifacts parse cleanly;
4. store smoke report in task report root.
