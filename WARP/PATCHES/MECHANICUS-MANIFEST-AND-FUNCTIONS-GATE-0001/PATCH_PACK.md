# MECHANICUS-MANIFEST-AND-FUNCTIONS-GATE-0001

## Purpose

Close the first two Mechanicus six-gate baselines: identity/manifest and functions registry.

This patch does **not** claim `MECHANICUS_ASSEMBLED` or `SIX_GATES_100_PERCENT_CLOSED`. It makes the claim boundaries machine-readable and binds current functions to evidence where available.

## Lands

- `ORGANS/MECHANICUS/MANIFEST.json`
- `ORGANS/MECHANICUS/FUNCTIONS.md`
- `ORGANS/MECHANICUS/MATRICES/MECHANICUS_FUNCTION_REGISTRY_V0_1.json`
- `ORGANS/MECHANICUS/MATRICES/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_MATRIX_V0_1.json`
- `ORGANS/MECHANICUS/TOOLS/build_mechanicus_manifest_and_functions_gate.py`
- `ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_manifest_and_functions_gate.py`
- `ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_PROSECUTOR_MATRIX_V0_1.json`
- `ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_CROWN_MATRIX_V0_1.json`

## Runtime outputs

- `ORGANS/MECHANICUS/RECEIPTS/mechanicus_manifest_and_functions_gate_receipt.json`
- `ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_SUMMARY_V0_1.json`
- `ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_REPORT_V0_1.json`
- `ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_REPORT_V0_1.md`

## Expected verdict

`PASS_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_READY`

## Meaning

- Mechanicus identity/manifest baseline is machine-readable.
- Mechanicus functions are classified with status and evidence references.
- Local model membrane remains `DEFERRED_AFTER_CORE_V1`.
- Mechanicus remains not assembled.
