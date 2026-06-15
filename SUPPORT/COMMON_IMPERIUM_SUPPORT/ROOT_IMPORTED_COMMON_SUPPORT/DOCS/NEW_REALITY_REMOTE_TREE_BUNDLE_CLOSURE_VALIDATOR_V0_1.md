# New Reality Remote Tree Bundle Closure Validator V0.1

Status: `ACTIVE_VALIDATOR_V0_1`

Tool:

```text
TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py
```

Schema:

```text
SCHEMAS/remote_tree_bundle_closure_receipt.schema.json
```

## Purpose

This validator proves that a New Reality closure task can tie together the active root, git remote, branch, local and remote heads, report bundle, bundle hash, native Astronomicon registry replay, invalid taskpack blocking, Ancient Empire read-only guard, and machine artifact encoding.

It uses git command evidence for remote visibility. It does not claim browser-level GitHub UI proof.

## Phases

### Prepare

```text
python TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py --phase prepare
```

Creates the task report directory and preliminary receipts. This phase is expected to dirty the worktree because it writes evidence files.

### Finalize

```text
python TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py --phase finalize
```

Run this only after the prepare commit has been pushed and the worktree is clean. The phase observes clean git equality first, then writes final receipts and the bundle. The written receipts record the accepted git self-reference limit.

### Verify

```text
python TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py --phase verify
```

Performs a no-write final verification after the final receipt commit has been pushed. It checks that `HEAD`, `origin/master`, and `git ls-remote origin refs/heads/master` agree, the worktree is clean, required outputs exist, and `sha256sums.txt` records the bundle SHA256.

## Required Outputs

The default report directory is:

```text
REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/
```

Required files:

```text
remote_tree_bundle_closure_receipt.json
native_registry_replay_receipt.json
invalid_taskpack_no_launch_recheck_receipt.json
ancient_readonly_guard_receipt.json
bundle_contract_receipt.json
final_remote_closure_receipt.json
validator_run_stdout.txt
RED_TEAM_VERDICT.json
CLAIM_LEDGER.json
CAPABILITY_SPLIT_RECEIPT.json
sha256sums.txt
task_report_bundle.zip
```

## Self-Reference Limit

The report bundle cannot contain a final receipt that already knows the SHA of the future commit that will contain that receipt. The bundle therefore contains `SELF_REFERENCE_LIMIT.txt`, while the external committed receipts record exact bundle path and SHA256. Final remote equality is proven by the no-write `verify` phase after push.
