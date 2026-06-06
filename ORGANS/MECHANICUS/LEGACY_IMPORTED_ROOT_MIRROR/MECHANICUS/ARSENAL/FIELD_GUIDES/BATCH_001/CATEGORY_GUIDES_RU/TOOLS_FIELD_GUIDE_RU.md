# TOOLS Field Guide (RU)

## Назначение категории
- Executable tools and CLIs.

## Сводка
- Всего capability: 14
- CANDIDATE: 11
- SANDBOX: 0
- CANON: 3
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-TOOL-COMMAND-GATEWAY-INTERNAL — command_gateway internal capability

- `capability_id`: CAP-TOOL-COMMAND-GATEWAY-INTERNAL
- `name`: command_gateway internal capability
- `category`: TOOLS
- `status`: CANON
- `plain_ru_description`: command_gateway internal capability: Allowlisted command execution with verdict receipt shape.
- `why_needed_for_imperium`: Constrains arbitrary command execution and captures evidence.
- `servitor_usage`: Разрешено в bounded-задачах при GATE_ACK и приложенных receipts.
- `local_agent_usage`: Локальный агент может применять в рамках узкого scope и доказуемой трассы.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-tool-command-gateway-internal
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; cap-tool-command-gateway-internal_receipt.json; src/imperium/security/command_gateway.py; src/imperium/security/__init__.py
- `task_scope_export_status`: EXPORT_ALLOWED_BOUNDED
- `owner_question_if_any`: -
- `notes`: Policy quality depends on maintained allowlist boundaries.

### CAP-TOOL-JSONSCHEMA — jsonschema

- `capability_id`: CAP-TOOL-JSONSCHEMA
- `name`: jsonschema
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: jsonschema: Schema-based JSON contract validator.
- `why_needed_for_imperium`: Prevents malformed contract/receipt artifacts.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-tool-jsonschema
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; cap-tool-jsonschema_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Cannot be treated as admitted without evidence.

### CAP-TOOL-NODE-NPM-NPX — Node/npm/npx candidate

- `capability_id`: CAP-TOOL-NODE-NPM-NPX
- `name`: Node/npm/npx candidate
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: Node/npm/npx candidate: Candidate JS runtime/toolchain lane.
- `why_needed_for_imperium`: Supports future visual/test ecosystem dependencies.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-tool-node-npm-npx
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; cap-tool-node-npm-npx_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: No package-management trust claim allowed yet.

### CAP-TOOL-PATH-POLICY-INTERNAL — path_policy internal capability

- `capability_id`: CAP-TOOL-PATH-POLICY-INTERNAL
- `name`: path_policy internal capability
- `category`: TOOLS
- `status`: CANON
- `plain_ru_description`: path_policy internal capability: Root-bounded path safety enforcement.
- `why_needed_for_imperium`: Prevents out-of-scope path traversal and root escape.
- `servitor_usage`: Разрешено в bounded-задачах при GATE_ACK и приложенных receipts.
- `local_agent_usage`: Локальный агент может применять в рамках узкого scope и доказуемой трассы.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-tool-path-policy-internal
- `receipt_gate_needed`: GATE-U02-SCOPE-BOUNDARY; cap-tool-path-policy-internal_receipt.json; src/imperium/security/path_policy.py; src/imperium/security/__init__.py
- `task_scope_export_status`: EXPORT_ALLOWED_BOUNDED
- `owner_question_if_any`: -
- `notes`: Callers must use policy functions consistently.

### CAP-TOOL-PYTEST — pytest

- `capability_id`: CAP-TOOL-PYTEST
- `name`: pytest
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: pytest: Python regression test runner.
- `why_needed_for_imperium`: Automates repeatable behavioral checks.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-tool-pytest
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; cap-tool-pytest_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Not admitted as available in this foundation task.

### CAP-TOOL-RECEIPT-MODELS-VALIDATORS — receipt models / validators internal capability

- `capability_id`: CAP-TOOL-RECEIPT-MODELS-VALIDATORS
- `name`: receipt models / validators internal capability
- `category`: TOOLS
- `status`: CANON
- `plain_ru_description`: receipt models / validators internal capability: Structured receipt model and validator helpers.
- `why_needed_for_imperium`: Normalizes PASS/WARN/FAIL/BLOCKED evidence semantics.
- `servitor_usage`: Разрешено в bounded-задачах при GATE_ACK и приложенных receipts.
- `local_agent_usage`: Локальный агент может применять в рамках узкого scope и доказуемой трассы.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-tool-receipt-models-validators
- `receipt_gate_needed`: GATE-U04-EVIDENCE-RECEIPT; cap-tool-receipt-models-validators_receipt.json; src/imperium/receipts/model.py; src/imperium/receipts/validator.py; src/imperium/receipts/__init__.py
- `task_scope_export_status`: EXPORT_ALLOWED_BOUNDED
- `owner_question_if_any`: -
- `notes`: Validator quality depends on contract coverage.

### TOOLS_CANDIDATE_CHECK_WORKFLOW — candidate check workflow

- `capability_id`: TOOLS_CANDIDATE_CHECK_WORKFLOW
- `name`: candidate check workflow
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: candidate check workflow: Mass intake candidate for candidate check workflow in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-candidate-check-workflow
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; tools-candidate-check-workflow_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### TOOLS_COMMAND_GATEWAY — command gateway

- `capability_id`: TOOLS_COMMAND_GATEWAY
- `name`: command gateway
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: command gateway: Mass intake candidate for command gateway in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-command-gateway
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; tools-command-gateway_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### TOOLS_COMMIT_PUSH_WORKFLOW — commit push workflow

- `capability_id`: TOOLS_COMMIT_PUSH_WORKFLOW
- `name`: commit push workflow
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: commit push workflow: Mass intake candidate for commit push workflow in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-commit-push-workflow
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; tools-commit-push-workflow_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### TOOLS_GIT — Git

- `capability_id`: TOOLS_GIT
- `name`: Git
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: Git: Mass intake candidate for Git in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-git
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; tools-git_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### TOOLS_PATH_POLICY — path policy

- `capability_id`: TOOLS_PATH_POLICY
- `name`: path policy
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: path policy: Mass intake candidate for path policy in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-path-policy
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; tools-path-policy_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### TOOLS_RECEIPT_VALIDATOR — receipt validator

- `capability_id`: TOOLS_RECEIPT_VALIDATOR
- `name`: receipt validator
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: receipt validator: Mass intake candidate for receipt validator in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-receipt-validator
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; tools-receipt-validator_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### TOOLS_SCOPE_REVIEW_TOOL — scope review tool

- `capability_id`: TOOLS_SCOPE_REVIEW_TOOL
- `name`: scope review tool
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: scope review tool: Mass intake candidate for scope review tool in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-scope-review-tool
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; tools-scope-review-tool_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### TOOLS_TASKPACK_DOSSIER_BUILDER — taskpack dossier builder

- `capability_id`: TOOLS_TASKPACK_DOSSIER_BUILDER
- `name`: taskpack dossier builder
- `category`: TOOLS
- `status`: CANDIDATE
- `plain_ru_description`: taskpack dossier builder: Mass intake candidate for taskpack dossier builder in TOOLS.
- `why_needed_for_imperium`: Mass intake seed for TOOLS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:tools-taskpack-dossier-builder
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; tools-taskpack-dossier-builder_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.
