# TASK SPEC

## Task ID

TASK-NEWREALITY-IMPERIAL-IDE-WORKBENCH-WARP-METAOS-INTEGRATION-PC-V0_2

## Mode

CONTROLLED_WRITE_WITH_VALIDATED_PUSH.

This task is PC only.

This is a triple integration task.

It must use the three bundled source ZIPs as candidate foundations and carefully compile them into Imperium New Reality:

1. Imperial IDE Workbench;
2. WARP Zone;
3. MetaOS Orchestration.

The Servitor task is a thin, precise, safe, working compilation and wiring task.

Do not manually scatter files.
Do not replace the current kernel.
Do not enable unsafe execution.
Do not claim a full finished IDE.

## Bundled source archives

This taskpack includes:

- SOURCE_BUNDLES/IMPERIAL_IDE_WORKBENCH_V0_1.zip
- SOURCE_BUNDLES/IMPERIUM_WARP_ZONE_V0_1.zip
- SOURCE_BUNDLES/IMPERIUM_METAOS_ORCHESTRATION_V0_1.zip

The Servitor must treat these archives as candidate input bundles.

The Servitor must record their SHA256 values and inventories before import.

Known expected SHA256 values:

- Workbench: 9ffe60b0e89c8af9eae402782a05457d55fa29c36161d89806da7c751a51ea63
- WARP: e228952d1bb669a4a6d82d42036d63428692eabfa48b6317bce8f6ff0e9c9942
- MetaOS: 06c06f678a2acc3879cc6049a1d3ade758773a67cb869752bfa5b42359cf1704

Hash mismatch is BLOCK unless the mismatch is fully explained and Owner accepts it.

## Strategic architecture

Imperium New Reality is the kernel.

Imperial IDE is the management and development surface over that kernel.

Workbench is the owner-facing cockpit.

WARP is the hot development zone inside the IDE.

MetaOS is the orchestration brain for routing, thin servitors, organ chronicles, budget-aware execution, and Administratum bundle gates.

Mechanicus is the tool guardian and validator.

Astronomicon is the task entry and registry authority.

Administratum is the bundle release and continuity authority.

Inquisition blocks fake-green and unsafe execution.

## Phase A: preflight

Required:

- Resolve current git root.
- Record git status.
- Record HEAD and origin/master.
- Confirm HEAD equals origin/master or record exact status.
- Confirm governance is CANON_ACTIVE.
- Confirm current Imperial IDE control shell exists.
- Confirm Mechanicus foundation exists.
- Locate bundled source archives inside registered taskpack extraction.
- Record source ZIP paths, sizes, SHA256, and root inventories.
- Confirm no local route config, runtime directory, secret, or deleted old artifact is staged.
- Confirm VM2 and VM3 are not required.

Stop if source archives cannot be located.

## Phase B: candidate extraction plan

Do not extract to repository root.

Do not replace the existing Imperial IDE shell.

Import destinations:

- Workbench -> ORGANS/IMPERIAL_IDE/WORKBENCH/
- WARP -> ORGANS/IMPERIAL_IDE/WARP/
- MetaOS -> ORGANS/IMPERIAL_IDE/METAOS/

If destination already exists, merge carefully:

- preserve existing active files;
- write import receipts;
- avoid blind overwrite;
- if conflict exists, keep existing active file and stage candidate as *.candidate or under IMPORTED_SOURCE/ with explanation.

Required import receipts:

- workbench_candidate_import_receipt.json
- warp_candidate_import_receipt.json
- metaos_candidate_import_receipt.json

## Phase C: normalize candidate content to current canon

Required normalization:

- Governance references must be CANON_ACTIVE.
- Validated-push policy must match current Imperium law.
- CUSTODES references must remain candidate security layer or be routed through INQUISITION, not silently added as baseline organ.
- SAMPLE mode must be clearly labelled.
- Real execution flags must default to blocked.
- WPF remains candidate unless Windows build receipt exists.
- MetaOS real LLM backend remains disabled; stub runner must be labelled stub.
- Runtime paths must be ignored.
- Missing README or contract references must be fixed or documented.

Create or update:

- ORGANS/IMPERIAL_IDE/WORKBENCH/INTEGRATION_STATUS.json
- ORGANS/IMPERIAL_IDE/WARP/INTEGRATION_STATUS.json
- ORGANS/IMPERIAL_IDE/METAOS/INTEGRATION_STATUS.json

## Phase D: Workbench integration

Workbench must become a controlled surface over the existing Imperial IDE shell.

Required:

- Workbench files live under ORGANS/IMPERIAL_IDE/WORKBENCH.
- Workbench has README and Russian run-first guide if useful.
- Workbench launchers exist.
- Workbench bridge points to current repo through IMPERIUM_ROOT or discovered root.
- Workbench can run in safe TUI or GUI smoke mode.
- Sample mode is honest.
- Live mode is only claimed when live bridge loads.
- Workbench is registered in Imperial IDE shell panel registry or command palette.

Required launcher:

- ORGANS/IMPERIAL_IDE/run_imperial_workbench.ps1

Required shell commands or command-palette entries:

- workbench
- workbench-tui
- workbench-gui
- workbench-smoke
- workbench-status

## Phase E: WARP integration

WARP must become the hot development zone.

Required:

- WARP files live under ORGANS/IMPERIAL_IDE/WARP.
- WARP launcher exists.
- WARP status is ACTIVE_HOT_ZONE_CANDIDATE or ACTIVE_HOT_ZONE depending on smoke proof.
- WARP runtime paths are ignored.
- WARP writes remain isolated from kernel.
- WARP release gate produces release_manifest only.
- WARP cannot promote to kernel without future Owner gate.

Required launcher:

- ORGANS/IMPERIAL_IDE/run_warp_zone.ps1

Required shell commands or command-palette entries:

- warp
- warp-open
- warp-list
- warp-status
- warp-gate
- warp-smoke

Required panel:

- WARP panel in Imperial IDE shell registry.

## Phase F: MetaOS integration

MetaOS must become the orchestration candidate layer.

Required:

- MetaOS files live under ORGANS/IMPERIAL_IDE/METAOS.
- MetaOS has README and Russian run-first guide if useful.
- MetaOS smoke can run.
- MetaOS orchestrator remains script-first.
- Thin servitor runtime is imported as candidate runtime.
- Administratum bundle gate is wired as release gate.
- Organ chronicles are written only to safe report or runtime paths.
- Real LLM backend is not enabled.
- Token/cost claims are labelled candidate unless measured in live system.

Required launcher:

- ORGANS/IMPERIAL_IDE/run_metaos_smoke.ps1

Required shell commands or command-palette entries:

- metaos
- metaos-smoke
- metaos-route
- metaos-servitor
- metaos-bundle-gate
- metaos-chronicle

Required panel:

- MetaOS panel in Imperial IDE shell registry.

## Phase G: Mechanicus bridge wiring

Workbench, WARP, and MetaOS must use Mechanicus as bridge authority.

Required bridge outputs may include:

- ORGANS/MECHANICUS/IDE_BRIDGE/workbench_bridge_adapter.py
- ORGANS/MECHANICUS/IDE_BRIDGE/warp_bridge_adapter.py
- ORGANS/MECHANICUS/IDE_BRIDGE/metaos_bridge_adapter.py
- ORGANS/MECHANICUS/IDE_BRIDGE/workbench_warp_metaos_bridge_policy.json

Required behavior:

- load current tool registry;
- load current capability registry;
- load command policy;
- dry-run tool invocation;
- unknown tool returns BLOCKED;
- real execution returns BLOCKED unless future allowlist gate exists;
- every invocation attempt writes a receipt.

## Phase H: Administratum bundle gate wiring

Administratum must receive bundle-gate outputs from WARP and MetaOS.

Required outputs may include:

- ORGANS/ADMINISTRATUM/BUNDLE_GATES/README.md
- ORGANS/ADMINISTRATUM/BUNDLE_GATES/administratum_bundle_gate_adapter.py
- ORGANS/ADMINISTRATUM/BUNDLE_GATES/bundle_gate_policy.json

Required behavior:

- HELD when evidence is insufficient;
- RELEASED when mandatory evidence is present;
- record evidence level;
- record missing fields;
- do not release WARP work to kernel automatically.

## Phase I: Servitor capsule model

Workbench servitor capsules and MetaOS thin servitor runtime are both candidate execution models.

Allowed:

- import capsule model;
- import supervisor;
- import thin servitor runtime;
- run safe smoke;
- show capsule or thin-servitor state in Workbench or shell;
- write queues/results only under ignored runtime paths.

Forbidden:

- AllowReal;
- persistent background daemon;
- real external command execution through capsules;
- real LLM execution through MetaOS;
- autonomous production claims.

## Phase J: user workflow

The Owner must get simple workflow commands.

Required launchers:

- ORGANS/IMPERIAL_IDE/run_imperial_ide.ps1 must remain valid.
- ORGANS/IMPERIAL_IDE/run_imperial_workbench.ps1
- ORGANS/IMPERIAL_IDE/run_warp_zone.ps1
- ORGANS/IMPERIAL_IDE/run_metaos_smoke.ps1

Required docs:

- ORGANS/IMPERIAL_IDE/DOCS/WORKBENCH_WARP_METAOS_USER_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/WORKBENCH_WARP_METAOS_OPERATOR_FLOW.md
- ORGANS/IMPERIAL_IDE/DOCS/WARP_METAOS_RELEASE_GATE_MODEL.md
- ORGANS/IMPERIAL_IDE/DOCS/NEXT_REAL_EXECUTION_AND_LLM_GATE_PLAN.md

The docs must explain how the Owner can:

- open the IDE shell;
- open Workbench;
- enter WARP;
- run MetaOS smoke;
- inspect tasks and reports;
- invoke dry-run tools through Mechanicus;
- understand what is still blocked.

## Phase K: smoke and validation

Required smoke and validation:

- Python compile for imported Workbench Python files.
- Python compile for imported WARP Python files.
- Python compile for imported MetaOS Python files.
- WARP smoke passes or exact blocker is recorded.
- WARP TUI smoke passes or exact blocker is recorded.
- Workbench TUI or GUI smoke passes where environment permits, or exact blocker is recorded.
- Workbench bridge sample or live mode passes.
- MetaOS integrated smoke passes.
- Administratum bundle gate HELD and RELEASED behavior is tested.
- Mechanicus bridge dry-run remains safe.
- Unknown tool invocation returns BLOCKED.
- Unsafe shell remains blocked.
- AllowReal remains disabled.
- Live LLM backend remains disabled.
- Runtime directories are ignored.
- JSON files parse.

If GUI or WPF cannot be tested in the current execution environment, record a Windows smoke blocker but do not fake success.

## Phase L: reports

Create reports under:

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-WORKBENCH-WARP-METAOS-INTEGRATION-PC-V0_2/

Required reports:

- source_bundle_inventory.json
- workbench_candidate_import_receipt.json
- warp_candidate_import_receipt.json
- metaos_candidate_import_receipt.json
- workbench_normalization_receipt.json
- warp_normalization_receipt.json
- metaos_normalization_receipt.json
- workbench_smoke_receipt.json
- warp_smoke_receipt.json
- metaos_smoke_receipt.json
- mechanicus_triple_bridge_receipt.json
- administratum_bundle_gate_receipt.json
- servitor_runtime_integration_receipt.json
- launcher_integration_receipt.json
- runtime_gitignore_receipt.json
- safety_gate_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Phase M: promotion status

If gates pass, mark:

- Workbench: ACTIVE_SURFACE or ACTIVE_SURFACE_CANDIDATE with reason.
- WARP: ACTIVE_HOT_ZONE or ACTIVE_HOT_ZONE_CANDIDATE with reason.
- MetaOS: ACTIVE_ORCHESTRATION_CANDIDATE or ACTIVE_ORCHESTRATION_LAYER with reason.

Do not mark:

- full GUI IDE complete;
- real servitor execution enabled;
- live LLM backend enabled;
- WARP promotion to kernel enabled;
- unrestricted tool execution enabled.

## Phase N: commit and validated push

Commit and push are required for PASS.

Commit message must include:

TASK-NEWREALITY-IMPERIAL-IDE-WORKBENCH-WARP-METAOS-INTEGRATION-PC-V0_2

After push, record:

- commit SHA;
- origin/master SHA;
- git status;
- pushed files summary;
- post-push equality of HEAD and origin/master.

## Stop conditions

Stop with BLOCK if:

- bundled source archives cannot be found;
- bundled source archives cannot be safely extracted;
- imported files would overwrite active shell without safe conflict handling;
- task would require VM2 or VM3;
- unsafe arbitrary command execution is required;
- AllowReal must be enabled to pass;
- live LLM secrets are required;
- secrets or local configs would be staged;
- runtime directory would be staged;
- JSON validation fails and cannot be repaired;
- Python validation fails and cannot be repaired;
- push is rejected and cannot be safely resolved.
