# Servitor Entry Contract V0.1

## Purpose

Define how a Servitor enters the Officio body before any mutable task execution.

## Required Entry Inputs

1. `task_id`
2. `starting_head`
3. `allowed_write_paths`
4. `forbidden_paths`
5. `required_gates`
6. `expected_receipts`
7. `stop_conditions`

## Entry Sequence

1. Run git truth check at repo root.
2. Read required gate law files and taskpack core files.
3. Build `GATE_ACK` with explicit PASS/STOP/CLARIFY verdict.
4. Declare scope boundary and touched path intent.
5. Continue only when `GATE_ACK.verdict = PASS`.

## Stop Binding

Stop immediately if:
- HEAD mismatch;
- worktree contains unrelated dirty state;
- required files are missing;
- task requires forbidden path writes;
- PASS claim cannot be proven with receipts.

## Evidence

- `REPORTS/<TASK_ID>/GATE_ACK.md`
- `REPORTS/<TASK_ID>/receipts/git_truth_receipt.json`

## Status

`ACTIVE`
