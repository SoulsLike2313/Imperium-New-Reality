# TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5

This is a **repair taskpack** for PC Servitor.

Primary correction:
- The previous V0_3 task reported under `E:\IMPERIUM\ORGANS\MECHANICUS\REPORTS\...`.
- That is wrong for this phase.
- Current work is **NEW GENERATION ONLY**.
- Do not merge into old/main `ORGANS/`, old/main `SANCTUM/`, or `IMPERIUM_TEST_VERSION/`.

Owner meaning:
- We are building the form in `IMPERIUM_NEW_GENERATION`.
- Later, useful data from main and test versions may be absorbed through explicit audit/gates.
- Do not silently blend old main organs into New Generation.
- Mechanicus click must open a real operator panel.
- LIVE/raw terminal must be secondary, not the main operator experience.

Read order:
1. `00_OWNER_BRIEF_RU.md`
2. `01_TASK_SPEC.md`
3. `02_TASK_SPEC.json`
4. `03_SCOPE_LOCK.json`
5. `04_UI_INTERACTION_CONTRACT.md`
6. `05_ACCEPTANCE_GATES.json`
7. `06_EVIDENCE_REQUIREMENTS.md`
8. `07_EXECUTION_PROTOCOL.md`
9. `08_FINAL_REPORT_TEMPLATE_RU.md`

Assets:
- ASSETS/negative_v03_raw_terminal_primary_bad.png
- ASSETS/negative_v03_report_wrong_main_scope_path.png
- ASSETS/target_reference_mechanicus_operator_console.png
- ASSETS/prior_brain_overview_peripheral_organs_reference.png

Prior evidence:
- `PRIOR_EVIDENCE/sse_proof_check_v03_owner_uploaded.zip` if present.
