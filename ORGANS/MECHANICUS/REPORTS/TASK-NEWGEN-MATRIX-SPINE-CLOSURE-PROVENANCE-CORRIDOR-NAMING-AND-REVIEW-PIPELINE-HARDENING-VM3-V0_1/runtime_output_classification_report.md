# Runtime Output Classification Report

Task: `TASK-NEWGEN-MATRIX-SPINE-CLOSURE-PROVENANCE-CORRIDOR-NAMING-AND-REVIEW-PIPELINE-HARDENING-VM3-V0_1`

## Classes
- `SOURCE`
- `CURATED_EVIDENCE`
- `RUNTIME_EPHEMERAL`
- `REPEATED_RUNTIME_OUTPUT`
- `QUARANTINE`
- `PRIVATE_OR_SECRET_DO_NOT_COMMIT`

## Enforcement
- Validator requires `classification` and `commit_decision` for each runtime output.
- Repeated/private runtime outputs cannot be committed (`CAP_RUNTIME_OUTPUT_UNCLASSIFIED`).
