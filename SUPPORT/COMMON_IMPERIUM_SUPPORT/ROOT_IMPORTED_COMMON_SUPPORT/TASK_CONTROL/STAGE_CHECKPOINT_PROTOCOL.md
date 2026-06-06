# Stage Checkpoint Protocol V0.1

## Purpose

Stage checkpoints keep long tasks observable and owner-controlled.

Each checkpoint records:
- what stage was attempted;
- before/after state;
- touched files and diff summary;
- evidence links;
- warnings/errors/blockers;
- decision options for next move.

## Required minimal artifacts

- checkpoint JSON (`STAGE_CHECKPOINT.schema.json`)
- checkpoint markdown summary
- touched files list
- diff summary
- evidence references

## Decision gate

Every checkpoint must present owner decision options:
- ACCEPT
- REQUEST_FIX
- CONTINUE_WITH_NOTES
- STOP
- SPLIT_REQUIRED

## Enforcement

If blockers are present, checkpoint status cannot be READY_FOR_REVIEW.
If evidence links are missing, verdict cannot claim PASS.
