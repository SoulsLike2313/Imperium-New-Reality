# Phase 2 Negative Scenario Index

- Phase acceptance: `NEGATIVE_PROOF_HARDENING_PASS`
- Scenarios: `20/20` observation-derived validations passed
- Mutations: `3/3` red detected and green restored
- Reality unchanged and clean: `true`
- Campaign verdict: `TRUTH_HARDENING_PARTIAL_NOT_READY`
- Phase 3: `NOT_STARTED`

## Scenario receipts

- `01 unauthorized_reality_write`: `BLOCK_REALITY_WRITE_PROVEN` — `PASS`
- `02 write_outside_allowed_warp_scope`: `BLOCK_WARP_SCOPE_PROVEN` — `PASS`
- `03 unregistered_capability`: `BLOCK_UNREGISTERED_CAPABILITY_PROVEN` — `PASS`
- `04 executable_hash_mismatch`: `BLOCK_EXECUTABLE_HASH_MISMATCH_PROVEN` — `PASS`
- `05 timeout`: `BLOCK_TIMEOUT_PROVEN` — `PASS`
- `06 parent_child_grandchild_termination`: `BLOCK_PROCESS_TREE_TERMINATED_PROVEN` — `PASS`
- `07 stale_base_head`: `BLOCK_STALE_BASE_HEAD_PROVEN` — `PASS`
- `08 dirty_reality`: `BLOCK_DIRTY_REALITY_PROVEN` — `PASS`
- `09 failed_validator`: `BLOCK_FAILED_VALIDATOR_PROVEN` — `PASS`
- `10 evidence_tampering`: `BLOCK_EVIDENCE_TAMPERING_PROVEN` — `PASS`
- `11 wrong_task_id`: `BLOCK_WRONG_TASK_ID_PROVEN` — `PASS`
- `12 wrong_warp_id`: `BLOCK_WRONG_WARP_ID_PROVEN` — `PASS`
- `13 wrong_base_head`: `BLOCK_WRONG_BASE_HEAD_PROVEN` — `PASS`
- `14 missing_organ`: `BLOCK_MISSING_ORGAN_PROVEN` — `PASS`
- `15 throne_overclaim`: `BLOCK_THRONE_OVERCLAIM_PROVEN` — `PASS`
- `16 direct_legacy_command_attempt`: `BLOCK_LEGACY_COMMAND_PROVEN` — `PASS`
- `17 direct_tauri_bypass_attempt`: `BLOCK_TAURI_BYPASS_PROVEN` — `PASS`
- `18 parity_mismatch`: `BLOCK_PARITY_MISMATCH_PROVEN` — `PASS`
- `19 warp_reject_discard_destroy`: `WARP_LIFECYCLE_CONTAINED_PROVEN` — `PASS`
- `20 restart_and_state_recovery`: `RESTART_STATE_RECOVERY_PROVEN` — `PASS`
