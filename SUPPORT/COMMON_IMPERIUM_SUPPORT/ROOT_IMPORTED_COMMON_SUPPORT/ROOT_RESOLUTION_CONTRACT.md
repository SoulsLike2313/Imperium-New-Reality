# Root Resolution Contract

Status: `CANDIDATE_V0_1`
Owner organ: `MECHANICUS`
Support organs: `ASTRONOMICON`, `ADMINISTRATUM`, `INQUISITION`, `OFFICIO_AGENTIS`

## Purpose

New Reality scripts must resolve the active IMPERIUM root without guessing whether the runtime root is the Ancient Empire root (`E:/IMPERIUM`) or the New Reality root (`E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`).

## Active Root

The only active PC New Reality root admitted by this contract is:

```text
E:/IMPERIUM_NEW_GENERATION_NEW_REALITY
```

`E:/IMPERIUM` is Ancient Empire reference memory only. It must not be accepted as an active root.

## Resolution Order

Every resolver implementation must use this order:

1. Explicit CLI or function argument: `--repo-root` / `-RepoRoot`.
2. Environment variable: `IMPERIUM_NEW_REALITY_ROOT`.
3. Upward auto-discovery from a supplied start path or current working directory.

Upward auto-discovery must require all root markers:

- `EPOCH_MANIFEST.json`
- `NEW_REALITY_SCOPE_LOCK.md`
- `AGENTS.md`

The root is valid only when `EPOCH_MANIFEST.json` declares `epoch` as `NEW_REALITY` and its `active_root` points to the same resolved root.

## Ancient Empire Block

The resolver must reject:

- `E:/IMPERIUM`
- paths outside `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`
- roots missing the required marker files
- roots whose epoch manifest does not declare `NEW_REALITY`

Ancient Empire may be read only when a task explicitly grants reference access and records that access in receipts.

## Git Field Sanity Gate

Receipts that include git fields must validate:

- `git_head` is a 40-character hex commit id unless a receipt explicitly labels a detached short-head preview field.
- `git_branch` is a single-line branch name.
- neither field contains usage/help text, command output tables, prompts, shell errors, or empty strings.

Malformed `git_head` or `git_branch` blocks clean PASS.

## Required Receipts

Tasks using this contract must produce:

- `root_resolution_receipt.json`
- `root_resolution_smoke_receipt.json`
- `git_field_sanity_gate_receipt.json`
- `ancient_empire_no_mutation_receipt.json`
- `runtime_candidate_patch_or_classification_receipt.json` when adapting prior candidates

## Capability Boundary

Root resolution helpers are `LOCAL_SCRIPT_FIRST` once they have a replay command and smoke receipt. Any manual reasoning about whether a root is safe remains `AGENT_REASONING_ONLY` until converted into a script-first checker.
