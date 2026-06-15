# CONTEXT PACK CONSUMPTION HARNESS CONTRACT

The harness must be script-first and replayable.

Recommended command shape:

```bash
python3 IMPERIUM_NEW_GENERATION/BLOCK_SPINE/TOOLS/consume_task_context_pack_v0_1.py \
  --repo-root . \
  --context-pack IMPERIUM_NEW_GENERATION/BLOCK_SPINE/REPORTS/TASK-NEWGEN-BLOCK-SPINE-CONTEXT-PACK-AND-LLM-FOCUS-OPTIMIZATION-VM3-V0_1/task_context_pack_v0_1.json \
  --out IMPERIUM_NEW_GENERATION/BLOCK_SPINE/REPORTS/TASK-NEWGEN-STAGE2-MICROPILOT-VM3-CONTEXT-PACK-EXECUTION-V0_1
```

The exact paths may be adapted to the repository reality.

## Required behavior

- Do not recursively read the whole repo.
- Read mandatory context list from the JSON pack.
- Record missing files as evidence.
- Hash every consumed file.
- Count bytes and approximate characters.
- Build organ usage summary from paths.
- Write receipts in the output directory.
- Exit nonzero if required critical files are missing.

## Manual read logging

Any extra manual reads outside the context pack must be recorded in:

`manual_read_log.jsonl`

Each line must include:

- timestamp
- path
- reason
- whether it was inside the context pack
- whether it changes the context economy claim

## Baseline measurement

The broad baseline must be metadata-based or bounded enumeration. It must not become a hidden broad read.
