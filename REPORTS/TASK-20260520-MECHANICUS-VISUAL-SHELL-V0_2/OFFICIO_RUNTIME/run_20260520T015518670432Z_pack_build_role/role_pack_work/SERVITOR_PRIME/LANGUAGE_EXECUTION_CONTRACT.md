# LANGUAGE EXECUTION CONTRACT

## Purpose
Enforce owner-facing language behavior after Officio role/settings ACK while preserving English machine artifacts.

## Activation Rule
- This contract is active only after valid `ACK_ROLE` and `ACK_SETTINGS`.
- If ACK is required but missing, execution must stop with:
  - `BLOCKED_OFFICIO_ACK_MISSING`

## Language Split After Officio ACK
| Surface | Required language |
|---|---|
| live Owner-facing work comments | Russian |
| final `OWNER COMMENTS` | Russian |
| technical identifiers | English |
| code / JSON keys / schema names | English |
| filenames / paths / commands | English |
| machine-readable artifacts | English |

## Violation Codes
- `WARN_RESPONSE_LANGUAGE_CONTRACT`
- `FAIL_RESPONSE_CONTRACT`
- `BLOCKED_OFFICIO_ACK_MISSING`
- `BLOCKED_ROLE_PACK_AUTHORITY_MISSING`
- `WARN_TASKPACK_ONLY_WORKAROUND_DETECTED`

## Checker Expectations V0.1
- Owner-facing prose in English after ACK is a contract violation.
- English machine artifacts must not be false-failed.
- Final response `OWNER COMMENTS` in English must fail response contract.
