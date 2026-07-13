# Phase 4 — Rust → Python Bridge Hardening

- Phase verdict: `RUST_PYTHON_BRIDGE_HARDENING_PASS`
- Campaign verdict: `TRUTH_HARDENING_PARTIAL_NOT_READY`
- Phase 5: `NOT_STARTED`
- Process-tree termination proven: `true`
- UI changes: `NONE`
- Land: `NOT_PERFORMED`

## Production boundary

Absolute registry-pinned `python.exe` and SHA-256 are revalidated before exact-argv, shell-free execution. CWD is the canonical WARP root, the inherited environment is cleared, timeout cleanup uses a Windows Job Object, and every completed process boundary writes an atomic bound receipt.

## Required targeted tests

- `phase4_01_admitted_absolute_python_works` — `PASS`
- `phase4_02_bare_python_is_rejected` — `PASS`
- `phase4_03_path_hijack_is_rejected` — `PASS`
- `phase4_04_executable_hash_mismatch_is_rejected` — `PASS`
- `phase4_05_cwd_escape_is_rejected_before_spawn` — `PASS`
- `phase4_06_shell_metacharacters_remain_inert_argv` — `PASS`
- `phase4_07_secret_like_environment_variables_are_excluded` — `PASS`
- `phase4_08_stdout_and_stderr_are_captured_separately` — `PASS`
- `phase4_09_timeout_kills_parent_child_and_grandchild` — `PASS`
- `phase4_10_bridge_receipt_has_task_warp_and_base_bindings` — `PASS`

## Validation

- `targeted_rust` — `PASS` — exit `0`
- `full_rust_tests` — `PASS` — exit `0`
- `cargo_check` — `PASS` — exit `0`
- `npm_build` — `PASS` — exit `0`
- `full_python_regression` — `PASS` — exit `0`
- `git_diff_check` — `PASS` — exit `0`

- Python regression: `67 passed`
- Reality/master unchanged and clean: `true`
- Checkpoint receipt hash: `9807c57fb38ad0226ae1565f3f7b8ba854fa970c39bd8ac7393dcdacd89e7e3f`

## Boundary

This checkpoint completes Phase 4 only. Phase 5 and every later campaign phase remain unstarted.
