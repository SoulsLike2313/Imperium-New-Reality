# Imperial IDE

Status: `FOUNDATION_ACTIVE`
Task: `TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1`

Imperial IDE is the future custom development zone over the New Reality kernel. This task creates contracts, schemas, registries, and workspace model only. It does not implement a full GUI application.

## Kernel Rule

The repository root and current-root `ORGANS/` are the kernel. IDE extensions must request tools through Mechanicus and produce receipts.

## Foundation Areas

- `CONTRACTS/` defines kernel, extension API, and tool invocation contracts.
- `SCHEMAS/` defines extension, workspace, tool invocation, and panel registry structures.
- `EXTENSIONS/extension_registry.json` seeds extension records.
- `WORKSPACE/workspace_model.json` seeds workspace state.
- `BRIDGES/mechanicus_bridge_contract.md` binds IDE tool invocation to Mechanicus.
