# Scope Locks And Caps

## Narrow scope

This task only attaches and verifies raw external review bundles, adjudicates the external-finalization cap, and records launcher-related next-task candidates.

## Forbidden expansions

- Do not implement IDE runtime.
- Do not implement WARP runtime.
- Do not implement browser automation runtime.
- Do not implement external API runtime.
- Do not implement AdsPower API actions.
- Do not claim freelance readiness.
- Do not claim trading readiness.
- Do not claim global clean PASS.
- Do not implement the Astronomicon launcher.
- Do not implement the Administratum continuity launcher.

## Cap handling

Adjudicate:

- `CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING_OR_NEEDS_FOLLOWUP`

Carry unless a separate accepted task closes them:

- `CAP_STAGE1_WITH_WARNINGS_ONLY`
- `CAP_NO_IDE_VISUAL_RELEASE_YET`
- `CAP_NO_WARP_RUNTIME`
- `CAP_DIRTY_START_OWNER_APPROVED_CONTINUATION`

## No fake green

Only set the external finalization cap to `CLOSED` if raw review bundles are attached, hash-checked, mapped to correct target heads, and referenced by final decision artifacts.

If evidence is partial, contradictory, or unreadable, set the cap to `NARROWED` or `CARRIED` and explain why.
