# COMMON_AGENT_CLI Contract

## Scope
This contract defines minimum UX and diagnostics behavior for organ-agent shells.

## Required Shell Guarantees
1. Operator always sees active organ, mode, git state, runtime state, and last run id.
2. Command model is short slash-first and stable.
3. Shell boundary is explicit: this shell is not a generic OS terminal.
4. Renderer truth is explicit and auditable.
5. Visual claims are backed by evidence artifacts.

## Command Grammar
Primary command grammar is defined by `command_palette_policy.json`.
Legacy command names may exist as aliases but cannot be primary help output.

## Layout Contract
Primary layout contract is defined in `ui_layout_spec.json`.
The shell must degrade cleanly on narrow terminal widths.

## Modes
Mode taxonomy and permissions are defined in `mode_switching_policy.json` and mode files in `MODES/`.

## Diagnostics
Renderer and color diagnostics must follow `renderer_contract.json` and `diagnostics_contract.json`.

## Heraldry
Original heraldry constraints are defined under `HERALDRY/`.
