# IMPERIUM Agent IDE

## V0.3 (Web-Shell Parity, React + TypeScript)

Task: `TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1`

### What is included

- Desktop IDE (`tkinter`) remains read-only and launchable for compatibility.
- React + TypeScript IDE-shaped surface under `REACT_IDE/`.
- Web projection server now serves React `dist/` when available (legacy fallback remains).
- Shared view model builder:
  - `VIEW_MODEL/ide_view_model_v0_2.json`
  - `VIEW_MODEL/dashboard_view_model_v0_1.json`
  - `VIEW_MODEL/block_view_model_v0_1.json`
- Desktop shell probe + decision receipts:
  - `DESKTOP_SHELL/tauri_probe_receipt.json`
  - `DESKTOP_SHELL/tauri_or_electron_decision_v0_1.json`
- Self-validator v0.2 that writes source/view-model/react/web/parity/mechanicus receipts.
- Playwright parity capture v0.2 with required screenshots and DOM truth marker snapshot.
- Block Foundation seed (`BLOCK_FOUNDATION/*`).
- Mechanicus tool registration entries for reusable tooling.

### Launch V0.2 desktop

```powershell
cd E:\IMPERIUM
.\IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\LAUNCH_AGENT_IDE_V0_2.ps1
```

### Launch web projection

```powershell
cd E:\IMPERIUM
.\IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\LAUNCH_AGENT_IDE_WEB_PROJECTION_V0_1.ps1
```

Then open: `http://127.0.0.1:4173/`

### Probe desktop shell toolchain

```powershell
cd E:\IMPERIUM
python IMPERIUM_NEW_GENERATION\AGENT_IDE\TOOLS\agent_ide_desktop_shell_probe_v0_1.py
```

### Build React IDE surface

```powershell
cd E:\IMPERIUM
python IMPERIUM_NEW_GENERATION\AGENT_IDE\TOOLS\agent_ide_react_build_check_v0_1.py
```

### Run self-validator v0.2

```powershell
cd E:\IMPERIUM
.\IMPERIUM_NEW_GENERATION\AGENT_IDE\TUI_OR_LAUNCHERS\RUN_AGENT_IDE_SELF_VALIDATOR_V0_2.ps1
```

## V0.2 / V0.1 Legacy Baseline

Legacy dual-surface/task outputs remain in place for compatibility and evidence continuity.

- `APP/agent_ide_app_v0_1.py`
- `APP/agent_ide_app_v0_2.py`
- `TUI_OR_LAUNCHERS/LAUNCH_AGENT_IDE_V0_1.ps1`
- `TUI_OR_LAUNCHERS/LAUNCH_AGENT_IDE_V0_1.cmd`
