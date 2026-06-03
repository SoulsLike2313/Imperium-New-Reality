# Mechanicus Arsenal Intake Foundation V0.1

This directory defines the controlled intake foundation for capabilities used by IMPERIUM_NEW_GENERATION.

Core law:
- No Arsenal card: capability does not exist for IMPERIUM.
- No validation gate: capability cannot become CANON.
- No receipt/evidence: capability usage is unproven.
- No source/license/trust note: capability cannot be promoted beyond CANDIDATE.

Primary documents:
- `ARSENAL_POLICY_V0_1.md`
- `ARSENAL_INTAKE_PROTOCOL_V0_1.md`
- `ARSENAL_STATUS_MODEL_V0_1.md`

Primary registries:
- `REGISTRY/arsenal_registry_v0_1.json`
- `REGISTRY/category_registry_v0_1.json`
- `REGISTRY/intake_queue_v0_1.json`

Primary schemas:
- `SCHEMAS/capability_card_schema_v0_1.json`
- `SCHEMAS/arsenal_registry_schema_v0_1.json`
- `SCHEMAS/validation_receipt_schema_v0_1.json`

Seed cards are stored under `CATEGORIES/<CATEGORY>/`.

Status discipline:
- `CANDIDATE`: known but untrusted.
- `SANDBOX`: testable under controlled scope.
- `CANON`: receipt/evidence-backed and admitted for bounded use.
- `QUARANTINE`: potentially useful but unsafe/unclear.
- `REJECTED`: not admitted.
