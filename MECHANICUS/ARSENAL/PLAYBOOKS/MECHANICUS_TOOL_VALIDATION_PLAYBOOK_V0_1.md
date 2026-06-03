# MECHANICUS TOOL VALIDATION PLAYBOOK V0.1

## Purpose
Repeatable Validation Batch corridor for foundational Mechanicus capabilities.

## Scope
- P0: Mechanicus spine (git, powershell, python, internal path/command/receipt capabilities)
- P1: code quality foundation (py_compile + optional external checkers)
- P2-lite: local evidence/search baseline (sqlite + fts5)
- P3: readiness detection only (playwright/node/npm/vite/react), no prototype comparison
- P5: LOCAL_LLM/CLOUD_LLM reserved, not validated here

## Hard Constraints
- No uncontrolled install
- No network provisioning
- No fake CANON
- No LOCAL_LLM/CLOUD_LLM activation
- No visual prototype comparison

## Runbook
1. Run truth checks and confirm clean start.
2. Write `GATE_ACK.md` with scope and stop conditions.
3. Run `mechanicus_capability_validator_v0_1.py`.
4. Confirm receipts generated under `ARSENAL/RECEIPTS/VALIDATION_BATCH_001/`.
5. Confirm reports generated under task report root.
6. Run fake-CANON detector and verify zero fake entries.
7. Export scope report for next Servitor tasks.
8. Check git diff stays inside declared paths.

## Required Outputs
- `validation_batch_manifest.json`
- `validation_results.json`
- `capability_status_change_report.json`
- `validation_receipts_index.json`
- `mechanicus_reusable_capabilities_report.json`
- `capability_scope_export_report.json`
- `fake_canon_detector_report.json`
- `inquisition_cleanliness_report.json`
- `administratum_evidence_map.json`
- `ghost_evolve_training_proof.json`
- `owner_questions_report.json`
- `closure_receipt.json`
- `FINAL_REPORT.md`

## Promotion Rule
- `CANDIDATE -> SANDBOX` only with PASS/PASS_WITH_WARNINGS receipt and bounded local usage.
- `SANDBOX -> CANON` deferred unless strong multi-run evidence exists.

## Stop Conditions
- Truth mismatch (root/branch/head)
- Forbidden path touch
- Missing evidence for PASS claim
- Fake-CANON introduced
- LLM/cloud activation required
- Install required without Owner approval
