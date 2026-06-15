# CONTINUITY_ROLE_PACK_VALIDATION_PROFILE_V0_1

Status: `CANDIDATE_V0_1`
Owner organ: `MECHANICUS`

## Purpose

Define minimum validation set for Owner Audit Card and continuity recipient bridge artifacts.

## Required checks

- JSON parseability:
  - `owner_audit_card_schema.json`
  - `continuity_recipient_selector_schema.json`
  - `role_pack_matrix.json`
  - role handoff receipts.
- Required fields present in:
  - Owner Audit Card schema,
  - recipient selector schema,
  - role matrix target entries.
- UTF-8 text readability for created markdown contracts.
- Required output list completeness against taskpack output requirements.

## Validation result classes

- `PASS_WITH_WARNINGS`: all required artifacts exist and parse, but inherited stage caps remain.
- `WARN`: one or more required checks missing.
- `BLOCK`: schema/receipt parse failure for mandatory machine artifact.

