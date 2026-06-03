# Checker Run Report

- task_id: TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1
- generated_at_utc: 05/25/2026 22:54:51
- verdict: PASS
- failed_count: 0

## Checker Commands
| command | exit_code | raw_log |
|---|---:|---|
| python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_owner_approved_tool_normalization_v0_1.py | 0 | IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/raw/validation/checker_1.txt |
| python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_owner_approval_matrix_v0_1.py | 0 | IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/raw/validation/checker_2.txt |
| python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_arsenal_foundation_v0_1.py | 0 | IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-CONTROLLED-INSTALL-WAVE-001-PC-V0_1/raw/validation/checker_3.txt |

## Side-Effect Containment
- finding: Checker scripts mutated historical task report files by default output behavior.
- restoration: Restored ONLY unintended out-of-task historical report files back to HEAD.
- hardening_lesson: Checker scripts must not overwrite historical task reports by default; output must go to current task report folder or explicit output path.
