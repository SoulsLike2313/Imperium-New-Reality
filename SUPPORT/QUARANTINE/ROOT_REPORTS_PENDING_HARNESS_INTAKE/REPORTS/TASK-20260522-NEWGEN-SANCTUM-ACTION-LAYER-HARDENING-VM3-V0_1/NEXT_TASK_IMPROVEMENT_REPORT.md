# Next Task Improvement Report

## KPD verdict
PLUS

## Context window verdict
OK

## What made this task harder than necessary?
- report filename drift and lifecycle timing mismatch (summary read before smoke file write)

## What should New Generation improve before the next task?
- canonical report filename contract + lifecycle order contract for in-flight summaries

## Which organ/zone should own each improvement?
- Mechanicus: automation and report lifecycle enforcement
- Officio: explicit language compliance evidence contract for runtime state
- Sanctum: better status lineage panel for action/report states

## Which validator/schema/registry should be added or hardened?
- action result schema with richer typed summary payload contract
- report lifecycle validator to enforce pre/post artifact expectations

## What should be moved from prompt into the system?
- standardized summary-state taxonomy and smoke expected-partial policy

## Was live Owner-facing Russian maintained?
- yes

## Recommended next task
- `TASK-20260522-NEWGEN-SANCTUM-ORGAN-DIALOGUE-DEMO-VM3-V0_1` (if this task closes PASS)
