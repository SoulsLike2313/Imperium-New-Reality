# Rejection Policy

Reject when any of the following is true:
- missing provenance (`REJECT_MISSING_PROVENANCE`);
- forbidden scope (`REJECT_FORBIDDEN_SCOPE`);
- mutation/deletion request (`REJECT_MUTATION_REQUEST`);
- runtime treated as canon (`REJECT_RUNTIME_AS_CANON`);
- fake green risk (`REJECT_FAKE_GREEN_RISK`);
- unknown high risk (`REJECT_UNKNOWN_HIGH_RISK`).

Every rejection must emit a receipt.
