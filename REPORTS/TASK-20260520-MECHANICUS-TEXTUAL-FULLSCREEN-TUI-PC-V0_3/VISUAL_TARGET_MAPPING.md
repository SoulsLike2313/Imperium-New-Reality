# VISUAL TARGET MAPPING

- task_id: `TASK-20260520-MECHANICUS-TEXTUAL-FULLSCREEN-TUI-PC-V0_3`
- reference: `ASSETS/VISUAL_TARGETS/mechanicus_operator_shell_visual_target.png`

## Target -> Implementation
- Top status strip with mission/head/status counters -> `TOP STATUS BAR` in V0.3 output and Textual header panel.
- Left activity timeline -> `LEFT WORK ZONE // CURRENT ACTIVITY` table.
- Right command palette with key hints -> `RIGHT COMMAND ZONE // OPERATOR PALETTE` with F1..F7 + R + ESC.
- Tool registry capability deck/table -> `TOOL REGISTRY // CAPABILITY OVERVIEW` with counts and rows.
- Bottom event summary bar -> `BOTTOM EVENT BAR` with report/receipt/event counters.
- Summary-first with details on demand -> default visual views + explicit `raw-*` detail mode only.

## Style Notes
- Mechanicus palette preserved through red/cyan/amber/green accents in rich/textual renderables.
- Fullscreen Textual app added for interactive terminal sessions; one-shot command path kept for automation evidence.
