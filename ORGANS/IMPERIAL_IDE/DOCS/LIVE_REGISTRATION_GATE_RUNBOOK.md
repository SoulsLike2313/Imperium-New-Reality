# Live Registration Gate Runbook

## Default

`register-taskpack` is a dry-run. It builds, validates, computes SHA256, checks local generated-path scope, finds the canonical Astronomicon skill, and writes a Station receipt without changing the task registry.

## Explicit live action

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py register-taskpack live "Task title"
```

The action is allowed only when:

- the source is inside `ORGANS/IMPERIAL_IDE/STATION/generated_taskpacks/`;
- all six Astronomicon root files exist;
- JSON and language gates pass;
- unsafe scope and secret checks pass;
- the canonical PC registration skill exists;
- the action is explicitly marked `live`.

The action can update `current_expected_task.json` and `task_registry.json`. Automated smoke therefore exercises the full precheck and records live mutation as intentionally skipped; it must not silently replace the active owner task.
