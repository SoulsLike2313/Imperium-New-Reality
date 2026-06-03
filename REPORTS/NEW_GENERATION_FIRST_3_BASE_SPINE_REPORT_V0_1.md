# NEW GENERATION FIRST 3 BASE SPINE REPORT V0.1

- task_id: `TASK-IMPERIUM-NEW-GENERATION-ORGAN-AGENT-BASE-SPINE-FIRST-3-V0_1`
- generated_at_utc: `2026-05-17T23:35:53.962233Z`
- scope: `IMPERIUM_NEW_GENERATION/**`
- owner_override_dirty_start: `true`

## Mandatory sources read before build
- `AGENTS.md`
- `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/IMPERIUM_NEW_GENERATION_10_ORGAN_AGENTS_20260518/README.md`
- `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/IMPERIUM_NEW_GENERATION_10_ORGAN_AGENTS_20260518/decision_manifest.json`
- `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/IMPERIUM_NEW_GENERATION_10_ORGAN_AGENTS_20260518/IMPERIUM_NEW_GENERATION_10_ORGAN_AGENTS_FORMATION_PLAN_EN_V0_2.pdf` (opened/read via page extraction)
- `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/IMPERIUM_NEW_GENERATION_10_ORGAN_AGENTS_20260518/IMPERIUM_NEW_GENERATION_10_ORGAN_AGENTS_FORMATION_PLAN_RU_V0_2.pdf` (opened/read via page extraction)

## Built foundation
- Full root spine for `IMPERIUM_NEW_GENERATION/` (CORE, PROTOCOLS, INTAKE, EXCHANGE, ORGAN_AGENTS, TOOLS, MEMORY, ARCHIVE, LEDGER, REPORTS, RECEIPTS, STRESS_TESTS, MERGE_BOARD).
- All 10 Organ-Agent folders created with required base files and required memory files.
- First 3 agents implemented in CLI base mode: `ADMINISTRATUM_AGENT`, `CUSTODES_AGENT`, `MECHANICUS_AGENT`.
- 7 remaining agents are honest skeletons with `SKELETON_ONLY_NOT_IMPLEMENTED`.

## CLI proof commands (executed)
- `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py agent status --agent ADMINISTRATUM`
- `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py agent status --agent CUSTODES`
- `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py agent status --agent MECHANICUS`
- `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py ask --agent CUSTODES --question IMPERIUM_NEW_GENERATION\EXCHANGE\ORGAN_BUS\questions\owner_demo_custodes_question_v0_1.json`
- `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py route --task IMPERIUM_NEW_GENERATION\INTAKE\normalized\demo_task_first_3_agent_route_v0_1.json`

## E2E route proof
- demo task: `IMPERIUM_NEW_GENERATION/INTAKE/normalized/demo_task_first_3_agent_route_v0_1.json`
- route receipt: `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\EXCHANGE\SERVITOR\receipts\route_receipt_0e5e6a3741a2.json`
- stress suite verdict: `PASS`
- stress suite path: `E:\IMPERIUM\IMPERIUM_NEW_GENERATION\STRESS_TESTS\NEW_GENERATION_FIRST_3_BASE_STRESS_RESULTS_V0_1.json`

## Units baseline (no filler generation)
- ADMINISTRATUM_AGENT: `65`
- CUSTODES_AGENT: `60`
- MECHANICUS_AGENT: `63`
- total first three: `188`
- future target: each of all 10 agents must later reach `>=3000` meaningful units.

## Manual owner verification commands
1. `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py agent status --agent ADMINISTRATUM`
2. `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py agent status --agent THRONE`
3. `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\imperium_ng_cli.py route --task IMPERIUM_NEW_GENERATION\INTAKE\normalized\demo_task_first_3_agent_route_v0_1.json`
4. `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\run_stress_tests.py`
5. `python IMPERIUM_NEW_GENERATION\TOOLS\agent_cli\count_agent_units.py`
