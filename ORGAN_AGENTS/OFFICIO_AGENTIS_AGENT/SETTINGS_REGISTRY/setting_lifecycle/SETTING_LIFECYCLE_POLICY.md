# Setting Lifecycle Policy

Allowed states:

- `DRAFT`
- `REVIEW`
- `ACTIVE`
- `DEPRECATED`
- `TOMBSTONE`

Rules:

- only schema-valid settings may become `ACTIVE`
- every transition requires a setting-change receipt
- `TOMBSTONE` is terminal
- rollback is allowed only with explicit evidence and receipt linkage

