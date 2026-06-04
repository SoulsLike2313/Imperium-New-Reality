# Task Report Bundle Matrix V0.1

Status: `CANDIDATE_V0_1`
Owner organ: `ADMINISTRATUM`

This matrix is a structural composition check for task report bundles. It
checks whether required evidence classes are represented by files in the report
directory, or by an adjacent receipt manifest when a proof file must remain next
to the final bundle because it describes the bundle itself.

## Required classes

| Class ID | Required evidence |
|---|---|
| `task_identity_and_report_metadata` | Task identity, focus packet, receipt, final report, or task-named report directory. |
| `commit_chain_identifiers` | Commit identifiers or local git closure receipt. |
| `git_closure_and_remote_closure_proof` | Git closure plus remote closure or remote-tree closure proof. |
| `worktree_clean_or_explicit_cap_receipt` | Clean worktree proof or an explicit cap/exception receipt. |
| `scope_lock_no_ancient_mutation_receipt` | Scope lock and no Ancient Empire mutation receipt. |
| `claim_ledger` | Machine claim ledger. |
| `capability_split_receipt` | Capability split or harnessability receipt. |
| `red_team_verdict` | Red-team verdict or explicit structural review verdict. |
| `final_owner_summary_boundary` | Final owner summary boundary or Officio localization reference. |
| `bundle_manifest_and_file_inventory` | Bundle manifest, evidence index, or file inventory. |
| `sha256_sums` | Hash sums for final bundle and included files where practical. |
| `adjacent_receipts_manifest` | Manifest for self-reference-limited adjacent proof files. |
| `administratum_composition_receipt` | Administratum bundle composition receipt. |

## Optional classes

| Class ID | Optional evidence |
|---|---|
| `screenshots_assets` | Screenshots, images, or UI evidence assets. |
| `web_research_dossier` | Web research dossier or source index. |
| `inquisition_review` | Inquisition review or fake-green check receipt. |
| `speculum_review` | Speculum review receipt. |
| `mechanicus_tool_receipts` | Mechanicus tool, validator, or candidate receipts. |
| `performance_cost_kpd_receipts` | Performance, cost, or KPD receipts. |

## Adjacent receipt logic

Some files cannot be fully self-contained inside the zip they describe. The gate
accepts an `adjacent_receipts_manifest.json` entry for these classes when the
listed adjacent file exists next to the bundle:

- `task_report_bundle.zip`
- `sha256sums.txt`
- `bundle_file_inventory.json`
- `administratum_bundle_composition_receipt.json`
- `git_closure_receipt.json`
- `remote_closure_receipt.json`

This is a composition pass with a recorded self-reference limit, not a semantic
truth pass.
