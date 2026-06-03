# Task Spec

## Objective

Create a reusable New Reality remote/tree/bundle closure validator and prove that New Reality remote closure is visible, consistent, and self-checking.

This task follows the successful New Reality final remote closure/native replay step. The new goal is not a large feature. The goal is a measuring instrument: every future task should be able to prove that the active repository, branch, remote HEAD, report bundle, SHA256, and closure receipts agree.

## Required implementation

Create these artifacts inside New Reality:

- `TOOLS/NEW_REALITY_VALIDATORS/validate_remote_tree_bundle_closure_v0_1.py`
- `SCHEMAS/remote_tree_bundle_closure_receipt.schema.json`
- `DOCS/NEW_REALITY_REMOTE_TREE_BUNDLE_CLOSURE_VALIDATOR_V0_1.md`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/remote_tree_bundle_closure_receipt.json`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/native_registry_replay_receipt.json`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/invalid_taskpack_no_launch_recheck_receipt.json`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/ancient_readonly_guard_receipt.json`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/bundle_contract_receipt.json`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/final_remote_closure_receipt.json`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/task_report_bundle.zip`
- `REPORTS/TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1/sha256sums.txt`

## Validator behavior

The validator must check at minimum:

1. Resolved active root is New Reality.
2. `git remote get-url origin` equals `https://github.com/SoulsLike2313/Imperium-New-Reality.git`.
3. Current branch is `master`.
4. Local `HEAD` exists and is a commit.
5. `origin/master` resolves.
6. `HEAD == origin/master` after final push.
7. `git ls-remote origin refs/heads/master` returns the same commit.
8. Worktree is clean for final closure.
9. Report bundle exists.
10. Report bundle SHA256 matches the value recorded in `sha256sums.txt`.
11. The bundle contains final closure receipt or explicitly records the accepted git self-reference limit.
12. Ancient Empire root is not mutated during the task.
13. Invalid taskpack fixture is blocked without launch card/start-task.
14. Machine bundle artifacts are English/UTF-8/no-BOM unless a declared Officio exception exists.

## Remote visibility note

Use git/remote verification as the required proof. Browser/web visual checks are optional. Do not claim browser-level GitHub UI proof unless it was actually performed and recorded.

## Git closure

This task should make normal local commits and push to `Imperium-New-Reality` remote. Final response must include commit links or commit identifiers, exact report bundle path, and SHA256.

The known git self-reference limit is allowed: a committed receipt cannot know the SHA of the commit that contains itself before that commit exists. A final no-write verification after push may record this as `PASS_WITH_SELF_REFERENCE_LIMIT` if all other checks pass.
