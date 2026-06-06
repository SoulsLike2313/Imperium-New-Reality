# OFFICIO BOOTSTRAP EXECUTION DIRECTIVE

## Purpose
Convert Officio role intake into active execution authority, not passive reference docs.

## Directive
- A Servitor must not begin serious implementation before Officio role/settings intake and explicit ACK artifact.
- After Officio ACK:
  - live Owner-facing progress commentary language is Russian;
  - final `OWNER COMMENTS` language is Russian;
  - machine artifacts remain English (code/json/schemas/paths/ids).
- Required authority files must be present in the generated role pack:
  - `OFFICIO_BOOTSTRAP_EXECUTION_DIRECTIVE`
  - `LANGUAGE_EXECUTION_CONTRACT`
  - `RESPONSE_CONTRACT`
  - `ROLE_SETTINGS_ACK_PROTOCOL`
  - `STOP_CONDITIONS`
  - `EVIDENCE_POLICY`

## Violation Codes
- `WARN_RESPONSE_LANGUAGE_CONTRACT`:
  - partial language drift with recoverable correction and truthful reporting.
- `FAIL_RESPONSE_CONTRACT`:
  - required response contract shape/language violated without correction.
- `BLOCKED_OFFICIO_ACK_MISSING`:
  - role/settings ACK is required but absent.
- `BLOCKED_ROLE_PACK_AUTHORITY_MISSING`:
  - generated role pack misses mandatory authority artifacts.
- `WARN_TASKPACK_ONLY_WORKAROUND_DETECTED`:
  - behavior rule exists only in taskpack, not Officio-owned contracts.

## ACK Extension Requirements
The ACK must confirm:
- role + mode admission;
- execution/communication contract refs;
- language execution contract ref;
- role settings ACK protocol ref;
- stop conditions accepted;
- language obligations accepted;
- machine artifact language boundary accepted.

## Scope Guard
This directive does not expand file scope or bypass stop conditions.
