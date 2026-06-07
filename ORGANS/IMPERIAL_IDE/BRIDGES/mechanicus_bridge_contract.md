# Mechanicus Bridge Contract

The Imperial IDE sends tool requests to Mechanicus, not directly to the shell.

## Current Foundation

- bridge mode: `DRY_RUN_FIRST`
- command policy: `ORGANS/MECHANICUS/REGISTRY/command_policy.json`
- tool registry: `ORGANS/MECHANICUS/REGISTRY/tool_registry.json`
- invocation schema: `ORGANS/IMPERIAL_IDE/SCHEMAS/ide_tool_invocation.schema.json`

Real execution is blocked until a future sandbox and allowlist task.
