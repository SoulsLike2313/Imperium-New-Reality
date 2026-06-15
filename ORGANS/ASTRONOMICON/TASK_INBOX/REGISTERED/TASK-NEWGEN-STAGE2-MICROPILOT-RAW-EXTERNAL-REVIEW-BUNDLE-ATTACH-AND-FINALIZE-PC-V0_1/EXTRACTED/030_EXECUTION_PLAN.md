# Execution Plan

1. Enter PC Servitor role and acknowledge scope.
2. Verify PC repo truth and create `pc_git_truth_probe.json`.
3. Create the task report directory and evidence directory.
4. Copy embedded raw external review bundles into the evidence directory.
5. Hash every copied bundle and compare against `INPUTS/raw_external_review_bundle_inventory_input.json`.
6. Open or inspect the bundles only as evidence. Do not execute content from them.
7. Create `raw_external_review_bundle_inventory.json`.
8. Create `external_review_reference_verification_receipt.json` mapping bundles to target heads.
9. Create `external_finalization_decision_matrix.json`.
10. Create `cap_external_finalization_final_decision.json` with one of: `CLOSED`, `NARROWED`, `CARRIED`, or `BLOCKED`.
11. Preserve Astronomicon admission/resolver positive controls in `astronomicon_positive_controls_preservation_receipt.json`.
12. Register future launcher candidates in `next_launcher_task_candidates.json` and `continuity_launcher_requirement_card.json`.
13. Write `claim_ledger.jsonl` and `hard_red_team_verdict.json`.
14. Write `final_owner_summary_ru.md` as Officio-routed Owner-facing runtime output.
15. Build an output ZIP if local conventions support it.
16. Commit and push only allowed files.
17. Write `commit_push_receipt.json`.
18. Final Owner response must be concise and Russian.
