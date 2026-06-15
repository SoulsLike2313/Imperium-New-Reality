# OUTPUT_REQUIREMENTS

## Required report files

Create under REPORTS/TASK-20260605-VM2-UBUNTU-CONTOUR-COST-GATE-READINESS-V0_1/ at minimum:

- FINAL_OWNER_SUMMARY_RU.md
- VM2_CONTOUR_READINESS_RECEIPT.json
- WINDOWS_PC_TO_VM2_COMPATIBILITY_RECEIPT.json
- STRATEGIUM_TASK_BUDGET_CARD.json
- STRATEGIUM_TASK_COST_RECEIPT.json
- STRATEGIUM_KPD_DELTA_RECEIPT.json
- SCHOLA_COST_REDUCTION_LESSON.json
- MECHANICUS_COST_CHECKER_TOOL_CARD.json or MECHANICUS_REGISTRATION_LIMITATION_RECEIPT.json
- ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json or POST_WORK_BUNDLE_LIMITATION_RECEIPT.json
- GIT_CLOSURE_RECEIPT.json
- REMOTE_CLOSURE_RECEIPT.json or POST_PUSH_NO_WRITE_PROOF.md

## Required repo artifacts

Create or update:

- ORGANS/STRATEGIUM/COST_GATE/TASK_BUDGET_CONTRACT_V0_1.md
- ORGANS/STRATEGIUM/COST_GATE/task_budget_card.schema.json
- ORGANS/STRATEGIUM/COST_GATE/task_cost_receipt.schema.json
- ORGANS/STRATEGIUM/COST_GATE/kpd_delta_receipt.schema.json
- ORGANS/STRATEGIUM/COST_GATE/TEMPLATES/TASK_BUDGET_CARD_TEMPLATE.json
- ORGANS/STRATEGIUM/COST_GATE/TEMPLATES/TASK_COST_RECEIPT_TEMPLATE.json
- ORGANS/STRATEGIUM/COST_GATE/TEMPLATES/KPD_DELTA_RECEIPT_TEMPLATE.json
- ORGANS/STRATEGIUM/COST_GATE/strategium_task_cost_checker_v0_1.py
- ORGANS/STRATEGIUM/COST_GATE/FIXTURES/positive_minimal/
- ORGANS/STRATEGIUM/COST_GATE/FIXTURES/negative_missing_budget_class/

## Final owner response

The final owner response must be Russian and include:

- task verdict;
- commit hash if committed;
- push status;
- VM2 readiness result;
- Windows/Ubuntu compatibility result;
- cost gate result;
- actual cost class;
- next task budget recommendation;
- warnings and limitations;
- exact paths to main receipts.

## GitHub index rule

Commit only safe index, contracts, schemas, checkers, fixtures, and report receipts. Do not commit large local-only bundles unless they are already accepted as small GitHub-safe artifacts.
