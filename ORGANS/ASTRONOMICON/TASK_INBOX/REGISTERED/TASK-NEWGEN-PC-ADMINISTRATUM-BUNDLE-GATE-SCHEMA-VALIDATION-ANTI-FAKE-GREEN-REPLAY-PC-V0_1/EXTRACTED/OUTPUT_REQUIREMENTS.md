# Output Requirements

Create all outputs inside the New Reality repository.

## Required report files

Under `REPORTS/TASK-NEWGEN-PC-ADMINISTRATUM-BUNDLE-GATE-SCHEMA-VALIDATION-ANTI-FAKE-GREEN-REPLAY-PC-V0_1/` produce:

- `administratum_bundle_gate_v0_2_receipt.json`
- `schema_validation_receipt.json`
- `anti_fake_green_fixture_receipt.json`
- `real_report_replay_receipt.json`
- `missing_items_and_invalid_fields_digest.json`
- `bundle_packager_receipt.json`
- `commit_chain_receipt.json`
- `git_closure_receipt.json`
- `remote_head_proof_receipt.json`
- `no_ancient_mutation_receipt.json`
- `servitor_control_chain_receipt.json`
- `RED_TEAM_VERDICT.json`
- `CLAIM_LEDGER.json`
- `CAPABILITY_SPLIT_RECEIPT.json`
- `IMPERIUM_QUESTION_PASS.json`
- `final_owner_summary.md`
- `sha256sums.txt`
- `task_report_bundle.zip`

If final self-reference proof files must remain adjacent to the bundle, also produce:

- `adjacent_receipts_manifest.json`
- `SELF_REFERENCE_LIMIT.md`

## Required source files

Under `ORGANS/ADMINISTRATUM/BUNDLE_GATE/` produce or update:

- `ADMINISTRATUM_BUNDLE_GATE_V0_2_CONTRACT.md`
- `TASK_REPORT_BUNDLE_SCHEMA_MATRIX.md`
- `administratum_bundle_gate_v0_2.py`
- `administratum_bundle_packager_v0_2.py`
- `README.md`
- `SCHEMAS/*.schema.json`
- `FIXTURES/**`

## Required final response details

The final response must include:

- Step name.
- Step verdict.
- Commit links/identifiers with labels.
- Exact report bundle path.
- Report bundle SHA256.
- Whether `origin/master == HEAD`.
- Whether worktree is clean.
