# PATCH PACK — IMPERIUM-TUI-WINDOWED-AQUARIUM-LAUNCHER-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/TUI`  
mode: `WINDOWED_OPERATOR_LAUNCHER`

## Purpose

Replace the insufficient menu-only console experience with a terminal-launched windowed operator launcher.

## Expected verdict

```text
PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_READY
```

## Run after pass

```powershell
pwsh SUPPORT/TUI/imperium_tui_window.ps1
```

## Must have

```text
function list
separate aquarium log pane
copy log button
clear log button
open log folder button
visible output for every called function
```

## Not claimed

```text
full IDE visual abstraction
graph/AAA visual layer resumed
background agent execution
Git land automation
```
