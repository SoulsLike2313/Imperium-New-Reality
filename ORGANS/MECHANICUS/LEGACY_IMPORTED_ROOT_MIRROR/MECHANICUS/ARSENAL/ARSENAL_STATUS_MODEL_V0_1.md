# ARSENAL STATUS MODEL V0.1

## Status Definitions

### CANDIDATE
Known useful idea/tool/practice that is not yet trusted.

### SANDBOX
Admitted for controlled local testing, but not canonical.

### CANON
Validated and evidence-backed for bounded use cases.

### QUARANTINE
Potentially useful but blocked due to safety, trust, or hygiene issues.

### REJECTED
Explicitly denied for use.

## Allowed Transitions
- `CANDIDATE -> SANDBOX`
- `SANDBOX -> CANON`
- `CANDIDATE/SANDBOX/CANON -> QUARANTINE`
- `CANDIDATE/SANDBOX/QUARANTINE -> REJECTED`

## Transition Guards
- To `SANDBOX`: test scope and safety notes are mandatory.
- To `CANON`: validation evidence path or receipt is mandatory.
- To `QUARANTINE`: risk or unresolved uncertainty is documented.
- To `REJECTED`: rejection reason and forbidden use notes are documented.

## Status Integrity Law
If mandatory fields, evidence, or trust notes are missing, status must be downgraded and cannot remain `CANON`.
