# VISUAL GAP REPORT

- task_id: `TASK-20260520-MECHANICUS-TUI-VISUAL-POLISH-MAX-PC-V0_4`
- reference_target: `mechanicus_operator_shell_visual_target.png`

## Achieved
- Distinct modes delivered: dashboard/tools/identity/check/raw.
- Raw JSON removed from default dashboard path.
- Tool registry semantics upgraded with clear status tokens and badge counters.
- Screenshot evidence pipeline operational with SVG outputs for dashboard/tools/raw (+ identity/check).

## Remaining Gaps (Honest)
- Textual interactive screenshots via keybinding `S` are implemented but not captured in this noninteractive evidence set; bundle uses deterministic `--screenshot` command path.
- Terminal box-drawing and font/rendering vary across hosts, so visual fidelity is high for TUI constraints but not pixel-identical to target image.
- Palette has reduced red dominance, but future Sanctum/web stage can provide finer gradient/shadow depth beyond terminal limits.

## Verdict
- `WARN_VISUAL_NOT_TARGET_GRADE` as expected for terminal-only phase, while functional/operational criteria pass.
