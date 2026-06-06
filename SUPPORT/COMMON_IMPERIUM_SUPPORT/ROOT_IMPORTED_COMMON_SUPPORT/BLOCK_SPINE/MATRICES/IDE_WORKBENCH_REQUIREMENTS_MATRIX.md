# IDE_WORKBENCH_REQUIREMENTS_MATRIX

Status: CANDIDATE_NOT_CANON
Owner organ: MECHANICUS
Support organs: STRATEGIUM, INQUISITION, OFFICIO_AGENTIS

| criterion_id | owner_organ | evidence_required | pass_logic | warn_logic | block_logic | score_or_delta | cap_mapping | remediation_path | forced_improvement |
|---|---|---|---|---|---|---|---|---|---|
| IW-01_DESIGN_ONLY_SCOPE | INQUISITION | ide requirement contracts + diff review | contracts only, no runtime IDE build | minor non-runtime scaffolding | desktop app implementation started | +25 | CAP_IDE_IMPLEMENTATION_STARTED_TOO_EARLY | remove implementation and keep contracts only | protects task scope |
| IW-02_TECH_STACK_CANDIDATES_DEFINED | MECHANICUS | tech stack candidates json | ts/react + tauri/rust + electron fallback all present | one candidate weakly justified | missing required stack candidate | +20 | CAP_IDE_WORKBENCH_REQUIREMENTS_MISSING | complete candidate file | aligns future build path |
| IW-03_TOOL_CHAMBER_CONTRACT_PRESENT | MECHANICUS | tool chamber contract json | tool/api surface contract exists with risk notes | partial risk notes | missing tool surface contract | +20 | CAP_TOOL_SURFACE_CONTRACT_MISSING | add contract and candidate cards | sets safe integration boundary |
| IW-04_RESOURCE_GOVERNOR_DEFINED | STRATEGIUM | resource governor requirements json | cpu/memory/token/runtime policies defined | policy present but not measurable | governor missing | +20 | CAP_RESOURCE_GOVERNOR_CONTRACT_MISSING | add measurable limits and caps | improves control-plane safety |
| IW-05_VALIDATOR_OFFLOAD_POLICY | MECHANICUS | local validator candidate card | compile/lint/type offload policy explicit | policy vague | no offload policy | +15 | CAP_NO_EFFICIENCY_DELTA | refine validator scope and metrics | reduces token waste |
