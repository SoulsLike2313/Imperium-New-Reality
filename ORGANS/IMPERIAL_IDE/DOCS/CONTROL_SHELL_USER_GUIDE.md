# Imperial IDE Control Shell User Guide

Task: `TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1`

The control shell is a local, read-only and dry-run-first management surface over the New Reality kernel.

## Start

```powershell
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1
```

The no-argument launcher opens the menu TUI. Non-interactive commands use the same launcher:

```powershell
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1 dashboard
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1 tools
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1 dry-run-tool mechanicus.doctor
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1 --smoke
```

## Output

CLI commands return JSON with `data` and a structured `receipt`. The shell does not mutate task registry, reports, tool registry, or workspace state.

## Safety

The shell does not expose arbitrary command execution. Tool requests are validated against Mechanicus registry and command policy and are dry-run only.
