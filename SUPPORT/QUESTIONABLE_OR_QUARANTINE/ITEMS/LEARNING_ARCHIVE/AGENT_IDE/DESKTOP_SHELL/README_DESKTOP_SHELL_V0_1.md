# Desktop Shell Boundary V0.1

Task: `TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1`

## Purpose

This directory stores desktop-shell probe and decision receipts for Tauri-preferred boundary planning.

## Probe command

```powershell
cd E:\IMPERIUM
python IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_desktop_shell_probe_v0_1.py
```

## Receipts

- `tauri_probe_receipt.json`
- `tauri_or_electron_decision_v0_1.json`

## Policy

- Prefer Tauri when available.
- Use Electron only as fallback if already available.
- Do not random-install global desktop tooling inside this task.
