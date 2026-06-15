# Mechanicus

Status: `CANON_ACTIVE_ULTRA_FOUNDATION`
Task: `TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1`

Mechanicus owns tool registry, capability registry, command policy, validation receipts, and safe tool invocation for the future Imperial IDE.

This foundation is deliberately dry-run first. It does not enable arbitrary shell execution.

## Core Files

- `REGISTRY/tool_registry.json` records tool identities and status.
- `REGISTRY/capability_registry.json` records capability status.
- `REGISTRY/command_policy.json` records command safety policy.
- `SCHEMAS/` contains JSON schemas for tools, capabilities, receipts, and invocations.
- `TOOLS/mechanicus_cli.py` is the local CLI entrypoint.
- `IDE_BRIDGE/` documents the future bridge between the IDE and Mechanicus.

## Supported Commands

```powershell
python ORGANS\MECHANICUS\TOOLS\mechanicus_cli.py doctor
python ORGANS\MECHANICUS\TOOLS\mechanicus_cli.py inventory
python ORGANS\MECHANICUS\TOOLS\mechanicus_cli.py validate-json
python ORGANS\MECHANICUS\TOOLS\mechanicus_cli.py dry-run-tool MECHANICUS_DOCTOR
```

Real tool execution remains blocked until a future owner-approved sandbox and command policy task.
