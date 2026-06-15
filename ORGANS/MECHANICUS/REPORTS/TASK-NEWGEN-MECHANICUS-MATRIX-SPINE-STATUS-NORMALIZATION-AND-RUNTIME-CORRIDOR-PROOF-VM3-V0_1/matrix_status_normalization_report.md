# Matrix Status Normalization Report

## Intent
Taskpack required `CANDIDATE_NOT_CANON` to stay allowed without warning when declared by schema/grammar, while keeping canon admission disabled.

## Implemented
- Added explicit policy file: `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/matrix_status_policy.json`.
- Validator now loads policy + schema and enforces synchronized status vocabulary.
- Removed alias-warning behavior for `CANDIDATE_NOT_CANON` and treats it as first-class allowed status.
- Added index-membership check (`MATRIX_ID_NOT_IN_INDEX`) so matrix registration must be explicit.

## Evidence
- Baseline prior task validator summary: WARN=4 (`MATRIX_STATUS_NONCANON_ALIAS`) and `PASS_WITH_WARNINGS`.
- Current validator run: `FAIL=0`, `WARN=0`, verdict `PASS`.
- Receipt paths:
  - `matrix_validator_run/matrix_spine_validation_summary.json`
  - `matrix_validator_run/matrix_spine_validation_report.md`

## Canon Boundary
`CANDIDATE_NOT_CANON` is accepted as status grammar only. Canon admission remains Doctrinarium authority and is not granted by this validator.
