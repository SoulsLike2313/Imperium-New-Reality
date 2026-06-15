# Imperial IDE

Status: `CONTROL_SHELL_ACTIVE`
Task: `TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1`

Imperial IDE is the future custom development zone over the New Reality kernel. It now includes a managed CLI and menu TUI control shell. It does not implement a full GUI application.

## Kernel Rule

The repository root and current-root `ORGANS/` are the kernel. IDE extensions must request tools through Mechanicus and produce receipts.

## Foundation Areas

- `CONTRACTS/` defines kernel, extension API, and tool invocation contracts.
- `SCHEMAS/` defines extension, workspace, tool invocation, and panel registry structures.
- `EXTENSIONS/extension_registry.json` seeds extension records.
- `WORKSPACE/workspace_model.json` seeds workspace state.
- `BRIDGES/mechanicus_bridge_contract.md` binds IDE tool invocation to Mechanicus.
- `SHELL/` provides the managed CLI, TUI, router, state, receipt model, panel registry, and command palette.
- `PANELS/` provides the first read-only dashboard panel adapters.


## Personal Launcher Home

The preferred owner-facing entry point is now the Imperial Launcher Home:

```powershell
python ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1
```

The terminal TUI remains available as fallback/debug:

```powershell
python ORGANS\IMPERIAL_IDE\WORKBENCH\TUI\imperial_tui.py
```

Launcher smoke:

```powershell
python ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py --smoke
```

## Control Shell

```powershell
python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_cli.py dashboard
python ORGANS\IMPERIAL_IDE\SHELL\imperial_ide_tui.py --smoke
powershell -ExecutionPolicy Bypass -File ORGANS\IMPERIAL_IDE\run_imperial_ide.ps1 dashboard
```

Tool requests remain dry-run first and are mediated by Mechanicus.


## Administratum Continuity Center V0.1

Continuity Pack is now an IDE-visible Administratum function. It previews and builds local ignored packs with manifest, receipt, owner summary, and Logos Prime handoff for safe transition into a new chat or audit handoff.

Commands:

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-preview h
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-build h
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-smoke
```

Safety: no commit, no push, no live LLM, no real servitor execution, no unsafe shell.
