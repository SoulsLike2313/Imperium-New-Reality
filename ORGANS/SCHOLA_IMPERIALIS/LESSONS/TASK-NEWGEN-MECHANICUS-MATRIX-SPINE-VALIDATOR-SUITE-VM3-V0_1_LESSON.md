# Schola Lesson — TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-VALIDATOR-SUITE-VM3-V0_1

## Reusable lesson
Schema contracts must be validated against real repository payloads before they are treated as runtime truth.

## Repeated mistake caught
- Text-level schema requirements were stricter than real matrix JSON fields, creating fake blocker noise.

## What became cheaper after this task
- New validator suite now gives replayable PASS/WARN/BLOCK evidence in one command.
- Negative fixtures provide quick regression proof for owner/status/red-team gate checks.

## What should be automated next
- Canonical status normalization migration (`CANDIDATE_NOT_CANON` -> canonical status vocabulary + explicit canon field).
- End-to-end runtime start-task corridor proof harness.
