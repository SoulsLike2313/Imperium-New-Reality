# ANTI CRUTCH CHECK LOG

- task_id: `TASK-20260520-ANTI-CRUTCH-PROTOCOL-VM2-V0_1`
- checked_at_utc: `2026-05-20T00:36:57.339202+00:00`

| Check | Status |
|---|---|
| valid_officio_no_crutch | PASS |
| valid_mechanicus_no_crutch | PASS |
| valid_doctrinarium_no_crutch | PASS |
| invalid_language_promote_officio | PASS |
| invalid_tool_promote_mechanicus | PASS |
| invalid_tool_bypass_blocked | PASS |
| invalid_law_promote_doctrinarium | PASS |
| invalid_fake_green_promote_doctrinarium | PASS |
| invalid_fake_green_promote_inquisition | PASS |

## Exit Codes
valid_exit_codes=0,0,0
invalid_exit_codes=1,2,1,2
taskpack_exit_code=1
check_text_invalid_prompt_only_exit_code=1

## Key Verdicts
- valid_officio: `['NO_CRUTCH_FOUND']`
- valid_mechanicus: `['NO_CRUTCH_FOUND']`
- valid_doctrinarium: `['NO_CRUTCH_FOUND']`
- invalid_language: `['DEBT_PROMOTE_TO_OFFICIO', 'WARN_TASKPACK_ONLY_WORKAROUND']`
- invalid_tool: `['BLOCKED_CANONICAL_AUTHORITY_BYPASSED', 'DEBT_PROMOTE_TO_MECHANICUS', 'WARN_TASKPACK_ONLY_WORKAROUND']`
- invalid_law: `['DEBT_PROMOTE_TO_DOCTRINARIUM', 'WARN_TASKPACK_ONLY_WORKAROUND']`
- invalid_fake_green: `['BLOCKED_CANONICAL_AUTHORITY_BYPASSED', 'DEBT_PROMOTE_TO_DOCTRINARIUM', 'DEBT_PROMOTE_TO_INQUISITION', 'DEBT_PROMOTE_TO_MECHANICUS', 'WARN_TASKPACK_ONLY_WORKAROUND']`
