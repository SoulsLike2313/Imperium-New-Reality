# MECHANICUS MEMORY LESSON 001

## Title
Validation first, promotion second.

## Context
Batch 001 validated foundational capabilities under strict no-install / no-fake-CANON rules.

## What Worked
- Script-first corridor (`validator`, `receipt_builder`, `scope_exporter`, `fake_canon_detector`).
- Per-capability receipts with explicit PASS/MISSING semantics.
- Conservative status promotion (`CANDIDATE -> SANDBOX` only with evidence).
- Dedicated Inquisition/Administratum hooks.

## Pain Points
- Duplicate card lines (CAP-* and folder cards) increase validation matrix size.
- Optional external tools can be missing even when foundational workflow is healthy.

## Permanent Rules
- Never claim CANON without evidence.
- Missing external tools are not failure if task forbids install.
- Reserved LOCAL_LLM/CLOUD_LLM lanes stay candidate-only until separate Owner gate.
- Always ship scope export for the next Servitor.

## Next Improvement
- Add stricter typing pass for new mechanicus_* scripts before deeper promotion.
