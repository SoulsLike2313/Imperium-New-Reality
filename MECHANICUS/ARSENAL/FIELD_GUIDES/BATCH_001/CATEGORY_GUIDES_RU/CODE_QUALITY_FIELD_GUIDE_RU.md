# CODE_QUALITY Field Guide (RU)

## Назначение категории
- Linting, type checking, and quality gates.

## Сводка
- Всего capability: 11
- CANDIDATE: 11
- SANDBOX: 0
- CANON: 0
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-CQ-PRECOMMIT — pre-commit candidate

- `capability_id`: CAP-CQ-PRECOMMIT
- `name`: pre-commit candidate
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: pre-commit candidate: Candidate commit-time hook enforcement.
- `why_needed_for_imperium`: Could prevent avoidable hygiene regressions.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-cq-precommit
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; cap-cq-precommit_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: No mandatory hook policy admitted.

### CAP-CQ-PYRIGHT-MYPY — pyright or mypy type safety candidate

- `capability_id`: CAP-CQ-PYRIGHT-MYPY
- `name`: pyright or mypy type safety candidate
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: pyright or mypy type safety candidate: Candidate static type-check lane.
- `why_needed_for_imperium`: Could detect interface/type drift earlier.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-cq-pyright-mypy
- `receipt_gate_needed`: GATE-U13-PYTHON-TYPE-SAFETY; cap-cq-pyright-mypy_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: No validated type profile in this task.

### CAP-CQ-RUFF — Ruff candidate

- `capability_id`: CAP-CQ-RUFF
- `name`: Ruff candidate
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: Ruff candidate: Candidate Python lint/format accelerator.
- `why_needed_for_imperium`: Could speed quality checks in bounded pipelines.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-cq-ruff
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; cap-cq-ruff_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: No canonical lint baseline approved yet.

### CODE_QUALITY_JSONSCHEMA — jsonschema

- `capability_id`: CODE_QUALITY_JSONSCHEMA
- `name`: jsonschema
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: jsonschema: Mass intake candidate for jsonschema in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-jsonschema
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-jsonschema_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### CODE_QUALITY_MYPY — mypy

- `capability_id`: CODE_QUALITY_MYPY
- `name`: mypy
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: mypy: Mass intake candidate for mypy in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-mypy
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-mypy_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### CODE_QUALITY_PRE_COMMIT — pre-commit

- `capability_id`: CODE_QUALITY_PRE_COMMIT
- `name`: pre-commit
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: pre-commit: Mass intake candidate for pre-commit in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-pre-commit
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-pre-commit_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### CODE_QUALITY_PYRIGHT — pyright

- `capability_id`: CODE_QUALITY_PYRIGHT
- `name`: pyright
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: pyright: Mass intake candidate for pyright in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-pyright
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-pyright_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### CODE_QUALITY_PYTEST — pytest

- `capability_id`: CODE_QUALITY_PYTEST
- `name`: pytest
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: pytest: Mass intake candidate for pytest in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-pytest
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-pytest_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### CODE_QUALITY_PY_COMPILE — py_compile

- `capability_id`: CODE_QUALITY_PY_COMPILE
- `name`: py_compile
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: py_compile: Mass intake candidate for py_compile in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-py-compile
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-py-compile_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### CODE_QUALITY_RUFF — ruff

- `capability_id`: CODE_QUALITY_RUFF
- `name`: ruff
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: ruff: Mass intake candidate for ruff in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-ruff
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-ruff_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### CODE_QUALITY_SCHEMA_FIRST_VALIDATION — schema-first validation

- `capability_id`: CODE_QUALITY_SCHEMA_FIRST_VALIDATION
- `name`: schema-first validation
- `category`: CODE_QUALITY
- `status`: CANDIDATE
- `plain_ru_description`: schema-first validation: Mass intake candidate for schema-first validation in CODE_QUALITY.
- `why_needed_for_imperium`: Mass intake seed for CODE_QUALITY.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:code-quality-schema-first-validation
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; code-quality-schema-first-validation_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.
