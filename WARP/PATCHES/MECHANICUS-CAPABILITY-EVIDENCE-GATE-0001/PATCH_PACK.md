# MECHANICUS-CAPABILITY-EVIDENCE-GATE-0001

## Purpose
Close Mechanicus G3 Capability Evidence baseline by binding every declared current function in `MECHANICUS_FUNCTION_REGISTRY_V0_1` to explicit reports/receipts/registries or to an explicit deferred/forbidden status.

## This patch does
- Adds Capability Evidence Gate law and matrix.
- Updates `ORGANS/MECHANICUS/MANIFEST.json` to manifest v0.3 and sets G3 to `PASS_BASELINE` only.
- Adds builder and validator for function evidence coverage.
- Produces receipt, summary, JSON report and MD report.
- Adds Custodes/Throne future audit matrices.

## This patch does not
- It does not assemble Mechanicus.
- It does not close personal validators, current truth/receipts, or residency/trust gates.
- It does not enable safe real execution.
- It does not enable local model membrane.

## Expected verdict
`PASS_MECHANICUS_CAPABILITY_EVIDENCE_GATE_READY`
