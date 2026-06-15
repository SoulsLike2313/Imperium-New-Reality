# Negative Fixtures Report

- Manifest: `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/negative_fixture_manifest.json`
- Fixture count: `24`
- All expected detections: `true`
- Validator summary:
  - `matrix_validator_run/matrix_spine_validation_summary.json`
  - verdict: `PASS`
  - fail: `0`
  - warn: `0`

Key newly enforced gates verified by fixtures:
- `CAP_EMPTY_IMPLEMENTATION_HEAD`
- `CAP_EMPTY_CLOSURE_BUNDLE_HEAD`
- `CAP_EMPTY_REMOTE_HEAD`
- `CAP_NO_INDEPENDENT_REPLAY`
- `CAP_CLAIM_LEDGER_MISSING`
- `CAP_RUNTIME_EXCLUDED_OUTPUT_WITHOUT_HASH`
- `CAP_HEADS_MIXED_OR_AMBIGUOUS`
