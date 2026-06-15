# Claim Ledger Required Closure Report

- Final closure verifier now requires:
  - `claim_ledger_path`
  - non-empty `claim_statuses_seen`
- Missing ledger coverage triggers mandatory cap:
  - `CAP_CLAIM_LEDGER_MISSING`
- Claim status vocabulary normalized to canonical Ghost_Evolve V2 set:
  - `TRUE`
  - `TRUE_WITH_SCOPE`
  - `PARTIAL`
  - `OVERCLAIM`
  - `UNKNOWN`
  - `FALSE_IF_CLAIMED`
  - `UNPROVEN`
  - `BLOCKED_BY_CAP`
- Negative fixture NF22 is detected (`true`).
