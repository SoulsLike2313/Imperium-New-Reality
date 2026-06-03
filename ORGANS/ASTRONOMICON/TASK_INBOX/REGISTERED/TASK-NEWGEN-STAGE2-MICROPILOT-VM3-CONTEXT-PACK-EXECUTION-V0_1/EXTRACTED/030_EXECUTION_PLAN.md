# EXECUTION PLAN

## Stage 0 - Admission and truth probe

1. Verify current HEAD is `cda220333299c82931f81beee461f6cb55974462`.
2. Verify branch and worktree status.
3. Verify remote sync state if possible.
4. Register or confirm Astronomicon task route.
5. Create a run report directory for `TASK-NEWGEN-STAGE2-MICROPILOT-VM3-CONTEXT-PACK-EXECUTION-V0_1`.

Expected receipt: `repo_truth_probe.json`.

## Stage 1 - Locate or build the task context pack

1. Locate the previous task context pack:
   `IMPERIUM_NEW_GENERATION/BLOCK_SPINE/REPORTS/TASK-NEWGEN-BLOCK-SPINE-CONTEXT-PACK-AND-LLM-FOCUS-OPTIMIZATION-VM3-V0_1/task_context_pack_v0_1.json`
2. If the builder supports a new task route, generate a fresh context pack for `TASK-NEWGEN-STAGE2-MICROPILOT-VM3-CONTEXT-PACK-EXECUTION-V0_1`.
3. If not, use the previous pack as a seed and create a micro-pilot context pack wrapper that clearly states it is seeded from the previous pack.
4. Do not broaden the read list manually without logging it.

Expected receipt: `task_context_pack_source_receipt.json`.

## Stage 2 - Build or harden context-pack consumption harness

Preferred new tool:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/TOOLS/consume_task_context_pack_v0_1.py`

Minimum behavior:

- Input: path to a context pack JSON.
- Output directory: run report directory.
- Reads mandatory context items that exist.
- Skips optional directories unless explicitly requested.
- Records missing files without crashing unless mandatory critical files are missing.
- Computes file count, byte count, approximate character count and SHA256 for consumed items.
- Classifies each item by organ when possible.
- Writes all required receipts.

## Stage 3 - Measure before/after context economy

Do not actually read the whole repository.

Measure a conservative broad-read baseline using file metadata or bounded directory enumeration only.

Recommended baseline candidates:

- `AGENTS.md`
- `IMPERIUM_NEW_GENERATION/`
- the 8 organ task participation folders
- the 8 organ block folders
- the previous task report directory

The baseline must state its method and caveats.

Expected receipt: `before_after_context_economy_delta.json`.

## Stage 4 - Organ block usage receipt

Create per-organ usage evidence:

- organ name
- files consumed
- digest read: true/false
- passport read: true/false
- task participation read: true/false
- used purpose
- missing or weak areas

Expected receipt: `organ_block_usage_receipt.json`.

## Stage 5 - Claim ledger and hard red-team

Create a line-delimited JSON claim ledger.

Each claim must include:

- claim_id
- claim_text
- status: `SUPPORTED`, `PARTIAL`, `UNSUPPORTED`, or `FORBIDDEN`
- evidence_files
- caveat

Hard red-team must downgrade if:

- broad repo reads occurred without logging;
- IDE/WARP/API runtime was touched;
- context economy is not measurable;
- script is not replayable;
- receipts are missing;
- worktree remains dirty.

## Stage 6 - Commit, push, closure

If verdict is PASS or PASS_WITH_WARNINGS:

1. Commit all task artifacts.
2. Push to origin.
3. Verify `origin/master == HEAD`.
4. Verify worktree clean.
5. Write `commit_push_receipt.json`.

No pending final without blocker.
