# Imperial IDE Operational Station

The Station is the operator-facing layer over the existing Imperial IDE shell, OPS task tooling, Astronomicon registration skill, Workbench, WARP, MetaOS, and Mechanicus policy surfaces.

## Entry points

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py station
python ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py
python ORGANS/IMPERIAL_IDE/WORKBENCH/GUI/imperial_gui_workbench.py
```

`station_router.py` exposes structured commands. `station_state.py` projects repository truth. `station_workflow.py` creates, validates, dry-run registers, and explicitly live-registers generated local PC taskpacks. Runtime taskpacks and receipts stay in ignored Station paths until canonical registration.

## Safety contract

- Dry-run registration is the default.
- Live registration requires the explicit `register-taskpack live` command.
- Live registration accepts only validated taskpacks generated under the Station output root.
- Real servitor execution, live LLM execution, arbitrary shell, remote registration, VM2, and VM3 actions are disabled.
- `HANDOFF_READY` is not `EXECUTION_COMPLETE`; the lifecycle records `EXECUTION_PENDING` truthfully.

See `RUN_FIRST_RU.md` for the shortest operator path.
