# Checker Side-Effect Note

- generated_at_utc: 2026-05-26T00:04:36Z
- finding: checker scripts wrote into historical task report folders as side effects.
- policy: these out-of-task mutations are not included in Wave001 commit and must be restored to HEAD.
- targets:
  - IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-INTAKE-FOUNDATION-PC-V0_1/arsenal_foundation_check_report.json
  - IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-OWNER-APPROVAL-MATRIX-PC-V0_1/matrix_check_report.json
  - IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-OWNER-APPROVED-TOOLS-REGISTRY-NORMALIZATION-PC-V0_1/normalization_check_report.json
