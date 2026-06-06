# Mechanicus Tool Expansion Playbook V0.1

## Цель
Повторяемый pipeline controlled toolbase expansion без silent installs.

## Шаги
1. Сбор candidate matrix:
`python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_candidate_builder_v0_1.py --task-id TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1`

2. Detection/receipt:
`python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_detection_runner_v0_1.py --task-id TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1`

3. Decision/promotion/approval queue:
`python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_decision_builder_v0_1.py --task-id TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1`

4. Scope refresh:
`python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_scope_refresh_v0_1.py --task-id TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1`

5. Finalize + evidence refresh:
`python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_tool_expansion_finalize_v0_1.py --task-id TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1`

## Guardrails
- No silent install.
- No React/Vite, no Playwright browser installs.
- No LLM/cloud activation.
- No private external context indexing.
- CANDIDATE -> SANDBOX only with local validation receipts.
- SANDBOX -> CANON запрещено в этом шаге.
