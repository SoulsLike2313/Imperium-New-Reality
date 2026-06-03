# LANGUAGE_BACKLOG_PHASED_REMEDIATION_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Inquisition`
Support organs: `Administratum`, `Mechanicus`, `Officio Agentis`

## Purpose

Define safe phased remediation behavior for legacy language backlog without broad rewrite.

## Criteria

### LBR-01
- Criterion ID: `LBR-01_SAFE_SLICE_REQUIRED`
- PASS logic: backlog slice is explicit, small (5-20), low-risk, and receipt-backed.
- WARN logic: slice exists but expected delta is partial.
- BLOCK logic: no slice, or broad mass rewrite attempted.
- Cap mapping: `CAP_PHASED_LANGUAGE_REMEDIATION_MISSING`, `CAP_UNSAFE_MASS_LANGUAGE_REWRITE`.

### LBR-02
- Criterion ID: `LBR-02_BEFORE_AFTER_EVIDENCE_REQUIRED`
- PASS logic: each changed item has before/after hash and action result.
- WARN logic: some items unchanged with explicit reason.
- BLOCK logic: edits without before/after evidence.
- Cap mapping: `CAP_BACKLOG_DELTA_MISSING`.

### LBR-03
- Criterion ID: `LBR-03_GLOBAL_CLEAN_PASS_FORBIDDEN`
- PASS logic: strict scope can pass while global status remains WARN with explicit caps.
- WARN logic: delta is positive but legacy debt remains.
- BLOCK logic: clean global PASS is claimed while backlog remains.
- Cap mapping: `CAP_GLOBAL_LANGUAGE_CLEAN_PASS_OVERCLAIM`.

## Evidence requirements

- `backlog_slice_selection_receipt.json`
- `language_remediation_actions.json`
- `language_backlog_delta_receipt.json`
- `post_remediation_independent_replay_receipt.json`
