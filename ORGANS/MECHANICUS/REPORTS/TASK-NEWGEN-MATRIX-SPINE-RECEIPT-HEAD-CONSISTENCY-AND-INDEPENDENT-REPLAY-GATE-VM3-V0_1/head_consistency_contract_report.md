# Head Consistency Contract Report

- Required head chain fields added and enforced in validator/schema/template:
  - `base_head`
  - `implementation_head`
  - `proof_head`
  - `closure_bundle_head`
  - `remote_head_after_bundle`
- Empty head fields now trigger mandatory caps:
  - `CAP_EMPTY_IMPLEMENTATION_HEAD`
  - `CAP_EMPTY_CLOSURE_BUNDLE_HEAD`
  - `CAP_EMPTY_REMOTE_HEAD`
- Mixed/ambiguous head semantics now trigger:
  - `CAP_HEADS_MIXED_OR_AMBIGUOUS`
- Commit URL evidence fields are required for provenance traceability.
- Negative fixtures NF07/NF08/NF19/NF24 are detected (`true`).
