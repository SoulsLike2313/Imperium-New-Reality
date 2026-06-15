# Acceptance Gates

## Local gates

- `new_reality_root_resolved`: PASS.
- `epoch_manifest_found`: PASS.
- `scope_lock_found`: PASS.
- `ancient_empire_not_mutated`: PASS.
- `native_astronomicon_registry_available`: PASS or WARN with exact reason if not touched by this task.

## Remote gates

- `remote_url_exact_match`: PASS only if origin URL equals `https://github.com/SoulsLike2313/Imperium-New-Reality.git`.
- `remote_push_performed`: PASS only if push succeeds.
- `remote_head_equals_local_head`: PASS only if `origin/master` or target branch equals local HEAD.
- `no_force_push`: PASS.
- `no_ancient_remote_push`: PASS.

## Closure gates

- `worktree_clean_after_commit`: PASS.
- `task_report_bundle_exists`: PASS.
- `task_report_bundle_sha256_recorded`: PASS.
- `final_answer_bundle_path_and_sha256`: PASS.
- `machine_artifacts_english_utf8_no_bom`: PASS.

## Verdict rules

- `CLEAN_PASS` is allowed only if all local, remote, and closure gates pass.
- `PASS_WITH_WARNINGS` is allowed if remote push fails due authentication/permission but all local and no-mutation gates pass.
- `BLOCK` is required if remote URL is not exact, remote contains unrelated history, Ancient Empire is mutated, or force push is required.
