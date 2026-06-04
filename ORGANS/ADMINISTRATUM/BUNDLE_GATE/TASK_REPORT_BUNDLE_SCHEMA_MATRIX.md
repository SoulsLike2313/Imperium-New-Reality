# Task Report Bundle Schema Matrix V0.2

Status: `CANDIDATE_V0_2`
Owner organ: `ADMINISTRATUM`

This matrix preserves the V0.1 composition classes and adds minimal field
contracts for required JSON receipt evidence. It is intentionally shallow:
Administratum validates structure, identity, root scope, and hash consistency;
it does not validate semantic truth.

## Required Classes

| Class ID | V0.2 field contract |
|---|---|
| `task_identity_and_report_metadata` | JSON evidence must include `task_id`; any `active_root` must equal the New Reality root. |
| `commit_chain_identifiers` | JSON evidence must include `task_id` and at least one commit/branch/self-reference field. |
| `git_closure_and_remote_closure_proof` | JSON evidence must include `task_id` and a worktree, remote, equality, or self-reference field. |
| `worktree_clean_or_explicit_cap_receipt` | JSON evidence must include `task_id` and either `worktree_clean`, `caps_triggered`, `cap_status`, or `self_reference_limit`. |
| `scope_lock_no_ancient_mutation_receipt` | JSON evidence must include `task_id`, `active_root`, and at least one no-Ancient core field. Mutation/write truthy values block. |
| `claim_ledger` | JSON evidence must include `task_id` and a `claims` array with claim/evidence/verdict rows. |
| `capability_split_receipt` | JSON evidence must include `task_id` and a verdict, owned-claims list, or capabilities list. |
| `red_team_verdict` | JSON evidence must include `task_id` and `verdict`. |
| `final_owner_summary_boundary` | JSON evidence must include `task_id` and an Officio/machine-language boundary field. Text evidence is allowed but Russian text inside machine bundle needs an Officio exception. |
| `bundle_manifest_and_file_inventory` | JSON evidence must include `task_id` and `included_files`; any `bundle_sha256` must match the bundle file when present. |
| `sha256_sums` | Text evidence must contain parseable SHA256 rows; rows for existing files must match file bytes. |
| `adjacent_receipts_manifest` | JSON evidence must include `task_id` and `adjacent_files`; listed adjacent files must exist. |
| `administratum_composition_receipt` | JSON evidence must include `task_id`, gate verdicts, and `authority_boundary=composition_schema_only`. |

## Negative Fixture Coverage

V0.2 fixtures cover:

1. missing required receipt file;
2. malformed required JSON;
3. missing `task_id`;
4. wrong `task_id`;
5. wrong/Ancient active root;
6. missing adjacent manifest with adjacent proof references;
7. stale or mismatched bundle SHA;
8. missing commit-chain/closure class;
9. forged no-Ancient receipt missing core fields;
10. Owner-facing Russian text in a machine bundle without Officio exception.

## Replay Policy

Real report replay is read-only. Old reports may block under V0.2 and should be
treated as migration candidates, not as failed historical execution, unless a
later semantic authority says otherwise.
