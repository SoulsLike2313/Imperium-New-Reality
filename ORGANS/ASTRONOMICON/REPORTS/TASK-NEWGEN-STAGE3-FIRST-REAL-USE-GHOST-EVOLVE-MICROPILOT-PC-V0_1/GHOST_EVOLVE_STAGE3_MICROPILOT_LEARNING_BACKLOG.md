# Ghost_Evolve Stage3 Micropilot Learning Backlog

Task ID: `TASK-NEWGEN-STAGE3-FIRST-REAL-USE-GHOST-EVOLVE-MICROPILOT-PC-V0_1`

## ST3-L01
- Problem: Astronomicon intake initially failed before task start due to missing/invalid route template and UTF-8 BOM.
- Organ: `ASTRONOMICON`
- Type: `INTAKE_GAP`
- Evidence: `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-STAGE3-FIRST-REAL-USE-GHOST-EVOLVE-MICROPILOT-PC-V0_1/stage3_bootstrap_repair_finding.json`
- Future fix: Add preflight encoding checker + auto-remediation command in intake toolchain.
- Blocks: `NEXT_MICROPILOT`
- Script-first candidate: `true`
- Recommended next task: `TASK-NEWGEN-STAGE3-ASTRONOMICON-BOOTSTRAP-HARDENING-UTF8-PREFLIGHT-PC-V0_1`

## ST3-L02
- Problem: Task start ACK template drift risk between corridor template and task-specific generated ACK shape.
- Organ: `ASTRONOMICON`
- Type: `RESOLVER_GAP`
- Evidence: `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_START_ACK_TEMPLATE.json`
- Future fix: Add schema lock + regression fixture for start ACK template.
- Blocks: `NEXT_MICROPILOT`
- Script-first candidate: `true`
- Recommended next task: `TASK-NEWGEN-STAGE3-ASTRONOMICON-STARTACK-SCHEMA-LOCK-PC-V0_1`

## ST3-L03
- Problem: Hard red-team and cap closure remain partially manual/report-local.
- Organ: `INQUISITION`
- Type: `CAP_GAP`
- Evidence: `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-STAGE3-FIRST-REAL-USE-GHOST-EVOLVE-MICROPILOT-PC-V0_1/hard_red_team_verdict.json`
- Future fix: Introduce immutable cap-state ledger writer/checker with cross-task index.
- Blocks: `REAL_USE_PILOT`
- Script-first candidate: `true`
- Recommended next task: `TASK-NEWGEN-STAGE3-INQUISITION-CAP-LEDGER-INDEX-PC-V0_1`

## ST3-L04
- Problem: Owner-facing RU/EN lane validation still depends on manual discipline.
- Organ: `OFFICIO_AGENTIS`
- Type: `ORGAN_GAP`
- Evidence: `IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/TASK_PARTICIPATION/KNOWN_GAPS_AND_NEXT_HOOKS.md`
- Future fix: Ship bundle-level RU/EN lane checker for report roots.
- Blocks: `NEXT_MICROPILOT`
- Script-first candidate: `true`
- Recommended next task: `TASK-NEWGEN-STAGE3-OFFICIO-RU-LANE-CHECKER-PC-V0_1`

## ST3-L05
- Problem: Manual Logos pipeline registration is candidate and lacks machine schema enforcement.
- Organ: `STRATEGIUM`
- Type: `MATRIX_GAP`
- Evidence: `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/MATRICES/MANUAL_LOGOS_PIPELINE_REGISTRATION_MATRIX.md`
- Future fix: Create schema + checker for manual pipeline registration record.
- Blocks: `REAL_USE_PILOT`
- Script-first candidate: `true`
- Recommended next task: `TASK-NEWGEN-STAGE3-STRATEGIUM-MANUAL-PIPELINE-SCHEMA-CHECKER-PC-V0_1`
