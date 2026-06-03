# REFERENCE_CODE Field Guide (RU)

## Назначение категории
- Internal reusable source modules and patterns.

## Сводка
- Всего capability: 9
- CANDIDATE: 8
- SANDBOX: 1
- CANON: 0
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-REF-PATHLIB-DISCIPLINE — pathlib / stdlib file operations discipline

- `capability_id`: CAP-REF-PATHLIB-DISCIPLINE
- `name`: pathlib / stdlib file operations discipline
- `category`: REFERENCE_CODE
- `status`: SANDBOX
- `plain_ru_description`: pathlib / stdlib file operations discipline: Safe stdlib path handling discipline.
- `why_needed_for_imperium`: Reduces shell-fragile path mutation logic.
- `servitor_usage`: Разрешено только в sandbox-контуре с явной валидационной receipt.
- `local_agent_usage`: Локальный агент может запускать только в экспериментальном контуре.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-ref-pathlib-discipline
- `receipt_gate_needed`: GATE-U13-PYTHON-TYPE-SAFETY; cap-ref-pathlib-discipline_receipt.json
- `task_scope_export_status`: EXPORT_ALLOWED_SANDBOX_ONLY
- `owner_question_if_any`: Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?
- `notes`: Current evidence is partial and module-centric.

### REFERENCE_CODE_CAPABILITY_CARD_SCHEMA — capability card schema

- `capability_id`: REFERENCE_CODE_CAPABILITY_CARD_SCHEMA
- `name`: capability card schema
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: capability card schema: Mass intake candidate for capability card schema in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-capability-card-schema
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-capability-card-schema_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### REFERENCE_CODE_ORGAN_CONSOLE_LAYOUT_REFERENCE — organ console layout reference

- `capability_id`: REFERENCE_CODE_ORGAN_CONSOLE_LAYOUT_REFERENCE
- `name`: organ console layout reference
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: organ console layout reference: Mass intake candidate for organ console layout reference in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-organ-console-layout-reference
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-organ-console-layout-reference_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### REFERENCE_CODE_OWNER_QUESTION_SCHEMA — owner question schema

- `capability_id`: REFERENCE_CODE_OWNER_QUESTION_SCHEMA
- `name`: owner question schema
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: owner question schema: Mass intake candidate for owner question schema in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-owner-question-schema
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-owner-question-schema_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### REFERENCE_CODE_READ_ONLY_SMOKE_HARNESS — read-only smoke harness

- `capability_id`: REFERENCE_CODE_READ_ONLY_SMOKE_HARNESS
- `name`: read-only smoke harness
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: read-only smoke harness: Mass intake candidate for read-only smoke harness in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-read-only-smoke-harness
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-read-only-smoke-harness_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### REFERENCE_CODE_SAFE_JSON_WRITE_HELPER — safe JSON write helper

- `capability_id`: REFERENCE_CODE_SAFE_JSON_WRITE_HELPER
- `name`: safe JSON write helper
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: safe JSON write helper: Mass intake candidate for safe JSON write helper in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-safe-json-write-helper
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-safe-json-write-helper_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### REFERENCE_CODE_SCOPE_EXPORT_SCHEMA — scope export schema

- `capability_id`: REFERENCE_CODE_SCOPE_EXPORT_SCHEMA
- `name`: scope export schema
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: scope export schema: Mass intake candidate for scope export schema in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-scope-export-schema
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-scope-export-schema_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### REFERENCE_CODE_STATUS_BADGE_SYSTEM — status badge system

- `capability_id`: REFERENCE_CODE_STATUS_BADGE_SYSTEM
- `name`: status badge system
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: status badge system: Mass intake candidate for status badge system in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-status-badge-system
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-status-badge-system_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### REFERENCE_CODE_VALIDATION_RECEIPT_SCHEMA — validation receipt schema

- `capability_id`: REFERENCE_CODE_VALIDATION_RECEIPT_SCHEMA
- `name`: validation receipt schema
- `category`: REFERENCE_CODE
- `status`: CANDIDATE
- `plain_ru_description`: validation receipt schema: Mass intake candidate for validation receipt schema in REFERENCE_CODE.
- `why_needed_for_imperium`: Mass intake seed for REFERENCE_CODE.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:reference-code-validation-receipt-schema
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; reference-code-validation-receipt-schema_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.
