# MECHANICUS TUI VISUAL POLISH V0.4 REPORT

- task_id: `TASK-20260520-MECHANICUS-TUI-VISUAL-POLISH-MAX-PC-V0_4`
- verdict: `PASS_WITH_WARNINGS`
- inferred_visual_status: `PASS_RICH_OPERATOR_SHELL`

## Outcome
- Visual shell upgraded from V0.3 to V0.4 with dedicated modes: dashboard/tools/identity/check/raw.
- Raw payload removed from default dashboard and moved to explicit raw/detail path.
- Command palette extended with screenshot command (`S` / `screenshot`) and noninteractive `shell --screenshot <mode>` flow.
- Tool registry switched to badge + semantic status presentation without SUMMARY pseudo-status rows.
- Path shortening integrated into default views to reduce noise.

## Evidence
- One-shot transcripts: dashboard/tools/identity/check/raw/raw-status.
- SVG screenshots: dashboard/tools/raw (+ optional identity/check).
- Renderer diagnostic, fake-shell proof, raw suppression report, and visual gap/mapping reports are included.

## Warnings
- `WARN_VISUAL_NOT_TARGET_GRADE`: terminal-only implementation remains bounded by TUI rendering limits versus image target aesthetics.
- Windows case-insensitive `STATE/state` + `RECEIPTS/receipts` index collision requires skip-worktree workaround noted in gate artifacts.
