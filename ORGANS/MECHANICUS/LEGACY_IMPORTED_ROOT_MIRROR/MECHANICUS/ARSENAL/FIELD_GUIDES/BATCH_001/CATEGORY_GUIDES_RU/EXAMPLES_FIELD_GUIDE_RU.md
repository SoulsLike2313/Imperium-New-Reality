# EXAMPLES Field Guide (RU)

## Назначение категории
- Reference examples and starter patterns.

## Сводка
- Всего capability: 9
- CANDIDATE: 8
- SANDBOX: 1
- CANON: 0
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-EXAMPLE-LOCAL-HTTP-DASHBOARD-SERVER — local HTTP dashboard server pattern

- `capability_id`: CAP-EXAMPLE-LOCAL-HTTP-DASHBOARD-SERVER
- `name`: local HTTP dashboard server pattern
- `category`: EXAMPLES
- `status`: SANDBOX
- `plain_ru_description`: local HTTP dashboard server pattern: Bounded local server pattern for dashboard smoke checks.
- `why_needed_for_imperium`: Supports repeatable local evidence capture loops.
- `servitor_usage`: Разрешено только в sandbox-контуре с явной валидационной receipt.
- `local_agent_usage`: Локальный агент может запускать только в экспериментальном контуре.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-example-local-http-dashboard-server
- `receipt_gate_needed`: GATE-U15-OPERATIONALITY-IMPACT; cap-example-local-http-dashboard-server_receipt.json
- `task_scope_export_status`: EXPORT_ALLOWED_SANDBOX_ONLY
- `owner_question_if_any`: Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?
- `notes`: Pattern is local-only and scenario-specific.

### EXAMPLES_CAPABILITY_SCOPE_EXAMPLE — capability scope example

- `capability_id`: EXAMPLES_CAPABILITY_SCOPE_EXAMPLE
- `name`: capability scope example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: capability scope example: Mass intake candidate for capability scope example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-capability-scope-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-capability-scope-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### EXAMPLES_EVIDENCE_REPORT_EXAMPLE — evidence report example

- `capability_id`: EXAMPLES_EVIDENCE_REPORT_EXAMPLE
- `name`: evidence report example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: evidence report example: Mass intake candidate for evidence report example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-evidence-report-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-evidence-report-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### EXAMPLES_INQUISITION_HYGIENE_SCAN_EXAMPLE — Inquisition hygiene scan example

- `capability_id`: EXAMPLES_INQUISITION_HYGIENE_SCAN_EXAMPLE
- `name`: Inquisition hygiene scan example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: Inquisition hygiene scan example: Mass intake candidate for Inquisition hygiene scan example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-inquisition-hygiene-scan-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-inquisition-hygiene-scan-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### EXAMPLES_MECHANICUS_TOOL_INTAKE_EXAMPLE — Mechanicus tool intake example

- `capability_id`: EXAMPLES_MECHANICUS_TOOL_INTAKE_EXAMPLE
- `name`: Mechanicus tool intake example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: Mechanicus tool intake example: Mass intake candidate for Mechanicus tool intake example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-mechanicus-tool-intake-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-mechanicus-tool-intake-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### EXAMPLES_ORGAN_CONSOLE_EXAMPLE — organ console example

- `capability_id`: EXAMPLES_ORGAN_CONSOLE_EXAMPLE
- `name`: organ console example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: organ console example: Mass intake candidate for organ console example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-organ-console-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-organ-console-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### EXAMPLES_OWNER_DECISION_QUEUE_EXAMPLE — Owner Decision Queue example

- `capability_id`: EXAMPLES_OWNER_DECISION_QUEUE_EXAMPLE
- `name`: Owner Decision Queue example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: Owner Decision Queue example: Mass intake candidate for Owner Decision Queue example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-owner-decision-queue-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-owner-decision-queue-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### EXAMPLES_TASKPACK_EXAMPLE — taskpack example

- `capability_id`: EXAMPLES_TASKPACK_EXAMPLE
- `name`: taskpack example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: taskpack example: Mass intake candidate for taskpack example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-taskpack-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-taskpack-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### EXAMPLES_VISUAL_GATE_EXAMPLE — visual gate example

- `capability_id`: EXAMPLES_VISUAL_GATE_EXAMPLE
- `name`: visual gate example
- `category`: EXAMPLES
- `status`: CANDIDATE
- `plain_ru_description`: visual gate example: Mass intake candidate for visual gate example in EXAMPLES.
- `why_needed_for_imperium`: Mass intake seed for EXAMPLES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:examples-visual-gate-example
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; examples-visual-gate-example_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.
