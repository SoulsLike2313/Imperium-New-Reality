# SHELL CONTRACT :: MECHANICUS_AGENT

Reference operator shell for Mechanicus must expose real operator context, not help-only smoke output.

Visual Shell V0.5 is summary-first with polished fullscreen Textual mode:
- compact operator cards by default;
- raw JSON only on explicit detail requests;
- Mechanicus identity accents and operator palette;
- Textual fullscreen app as default when dependencies and TTY are available;
- static rich/plain fallback when Textual is unavailable.

## Supported Shell Commands
- help
- status
- dashboard
- check
- where
- identity
- tools
- pack
- raw
- screenshot
- shell --once help
- shell --once status / dashboard / visual-status
- shell --once tools / visual-tools
- shell --once identity / visual-identity
- shell --once check / visual-check
- shell --once raw
- shell --once raw-status
- shell --once raw-tools
- shell --once raw-identity
- shell --once raw-check
- F1..F7 in Textual mode (status/tools/identity/check/where/pack/help)
- R in Textual mode for explicit raw/detail mode
- S in Textual mode for screenshot save
- shell --screenshot <mode> for SVG export in noninteractive flow
- shell --screenshot all for batch export (dashboard/tools/identity/check/raw)
- ESC in Textual mode for exit
- exit

## Visual Status
- PASS_RICH_OPERATOR_SHELL
- PASS_PLAIN_OPERATOR_SHELL
- WARN_PLAIN_FALLBACK
- BLOCKED_SHELL_NOT_IMPLEMENTED
- FAIL_FAKE_SHELL

## Required Operator Surfaces
- TOP STATUS BAR
- LEFT WORK ZONE
- RIGHT COMMAND ZONE
- TOOL REGISTRY
- BOTTOM EVENT BAR
- renderer mode visibility
- tool registry summary visibility
- command palette visibility
