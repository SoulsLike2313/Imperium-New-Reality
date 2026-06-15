# TASK BRIEF

## Task

`TASK-NEWGEN-STAGE2-MICROPILOT-VM3-CONTEXT-PACK-EXECUTION-V0_1`

## Purpose

Run the Stage 2 micro-pilot that proves the new Block Spine / context-pack layer is useful in practice.

The previous task built a context-pack foundation. This task must prove that a Servitor execution can consume compact task context instead of broad repo reading.

## Core proof

Build or harden a local, replayable context-pack consumption harness that:

1. Takes a task context pack JSON as input.
2. Reads only the listed mandatory context files unless explicitly permitted.
3. Records every context item consumed.
4. Maps consumed files to organ blocks.
5. Compares the compact context pack against a conservative broad-read baseline.
6. Produces evidence that the context-pack route is cheaper and narrower.
7. Records any manual or extra reads honestly.

## Required outputs

- `context_pack_consumption_receipt.json`
- `before_after_context_economy_delta.json`
- `organ_block_usage_receipt.json`
- `manual_read_log.jsonl`
- `llm_focus_claim_ledger.jsonl`
- `cap_carry_forward_receipt.json`
- `hard_red_team_verdict.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

## Expected implementation shape

A minimal script-first harness is preferred, for example:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/TOOLS/consume_task_context_pack_v0_1.py`

The exact filename may change if a better local convention already exists, but the script must be replayable and registered or referenced in receipts.

## Non-goals

- Do not implement IDE runtime.
- Do not implement WARP runtime.
- Do not connect external APIs.
- Do not run browser automation.
- Do not claim freelance readiness.
- Do not canonize Block Spine globally.
