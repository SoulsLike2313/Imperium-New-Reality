# BLOCK_STANDARD_V0_1

Status: CANDIDATE_NOT_CANON
Owner organ: DOCTRINARIUM
Support organs: OFFICIO_AGENTIS, ASTRONOMICON, ADMINISTRATUM, MECHANICUS, INQUISITION, STRATEGIUM, SCHOLA_IMPERIALIS

## Purpose

Define one compact and repeatable block contract so Servitor and large LLM workflows consume exact boundaries instead of broad repository browsing.

## Required block identity

- block_id
- block_type
- owner_organ
- purpose
- read_first_files

## Required zone model

- protected_zones: files and folders that require stronger change gates.
- editable_zones: files and folders allowed for routine changes.
- runtime_zones: files and folders for generated runtime artifacts and reports.

## Required contract model

- input_contracts
- output_contracts
- scripts_or_tools
- receipts
- matrices

## Required memory model

- memory_refs
- pain_memory_refs
- success_memory_refs
- improvement_request_refs

## Required governance model

- validation_gates
- context_budget
- forbidden_claims

## Minimal lifecycle

1. Define block manifest using schema.
2. Publish compact read-first and context digest.
3. Run task using context pack builder.
4. Run bloat detector and record caps.
5. Emit receipts and claim ledger entries.
6. Red-team the result before verdict.

## PASS expectations

- Every block can be loaded by compact digest first.
- Protected and editable zones are explicit.
- Context budget is measurable and enforced.
- Improvement requests are structured and replayable.
