# Imperial IDE Control Shell

Task: `TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1`
Status: `CONTROL_SHELL_ACTIVE_V0_1`

This stdlib-first shell exposes governance, Astronomicon tasks, reports, receipts, Mechanicus registries, extensions, workspace state, validation, and dry-run tool invocation.

It is not a full GUI IDE and does not expose unrestricted shell execution.

## Entrypoints

```powershell
python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py dashboard
python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_tui.py --smoke
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1 dashboard
```
