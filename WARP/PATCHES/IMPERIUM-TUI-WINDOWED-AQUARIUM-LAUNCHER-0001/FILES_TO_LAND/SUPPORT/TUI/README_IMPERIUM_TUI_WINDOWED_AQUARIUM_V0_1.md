# IMPERIUM TUI — Windowed Aquarium Launcher V0.1

patch_id: `IMPERIUM-TUI-WINDOWED-AQUARIUM-LAUNCHER-0001`

## Purpose

The previous console menu was not the desired shape.

This launcher is terminal-started, but opens a native Windows operator window:

```powershell
pwsh SUPPORT/TUI/imperium_tui_window.ps1
```

## Shape

```text
Left panel:
  function list in Russian

Middle/left details:
  selected function description

Right panel:
  separate aquarium log window

Buttons:
  Execute function
  Copy log
  Clear log
  Save window log
  Open logs folder
```

## Aquarium

Every function runs through the existing validated console TUI:

```text
python SUPPORT/TUI/imperium_tui.py --action <id>
```

The output is shown in the right log pane and the underlying action still writes:

```text
SUPPORT/TUI/LOGS/
SUPPORT/TUI/RECEIPTS/
```

## Not claimed

```text
full IDE visual abstraction
graph/AAA visual layer resumed
background agent execution
Git land automation
Great Nine assembled
Core v1 ready
```
