# VISUAL TARGET MAPPING

- task_id: `TASK-20260520-MECHANICUS-TUI-VISUAL-POLISH-MAX-PC-V0_4`
- visual_target_reference: `ASSETS/VISUAL_TARGETS/mechanicus_operator_shell_visual_target.png`

## Target -> V0.4 Implementation
- Compact top strip -> `TOP STATUS BAR` with sigil + shell version + mission clip.
- Left activity deck -> `LEFT WORK ZONE // CURRENT ACTIVITY` timeline table.
- Right command palette -> `COMMAND ZONE // OPERATOR PALETTE` with F1..F7, R, S, ESC and domain commands.
- Capability deck -> `TOOL REGISTRY // CAPABILITY OVERVIEW` with status badges and normalized semantic statuses.
- Bottom event bar -> `BOTTOM EVENT BAR` with shortened report/receipt paths and warning counters.
- Summary-first dashboard -> default `dashboard/status` mode hides raw payload panel.
- Explicit detail mode -> `raw` mode and `raw-*` one-shot commands expose detail payload only on demand.

## Mechanicus Identity Delta
- Stronger identity header with cog-sigil marker and copper accent line.
- Mission panel now includes forge motto and tooling identity line.

## Path Noise Reduction
- Default views render shortened repository-relative paths (`.../.../`) for high-density readability.
- Full absolute path payload remains available in raw/detail mode.
