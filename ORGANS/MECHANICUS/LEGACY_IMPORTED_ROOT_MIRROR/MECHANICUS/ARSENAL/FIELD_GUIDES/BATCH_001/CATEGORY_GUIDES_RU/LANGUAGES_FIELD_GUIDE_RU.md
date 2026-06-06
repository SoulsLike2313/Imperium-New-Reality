# LANGUAGES Field Guide (RU)

## Назначение категории
- Runtimes and programming language baselines.

## Сводка
- Всего capability: 9
- CANDIDATE: 8
- SANDBOX: 1
- CANON: 0
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-LANG-PYTHON312-RUNTIME — Python 3.12 runtime

- `capability_id`: CAP-LANG-PYTHON312-RUNTIME
- `name`: Python 3.12 runtime
- `category`: LANGUAGES
- `status`: SANDBOX
- `plain_ru_description`: Python 3.12 runtime: Default runtime for NewGen scripts and validators.
- `why_needed_for_imperium`: Reduces scripting baseline drift across tasks.
- `servitor_usage`: Разрешено только в sandbox-контуре с явной валидационной receipt.
- `local_agent_usage`: Локальный агент может запускать только в экспериментальном контуре.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-lang-python312-runtime
- `receipt_gate_needed`: GATE-ARSENAL-HOST-RUNTIME-VERIFY; cap-lang-python312-runtime_receipt.json
- `task_scope_export_status`: EXPORT_ALLOWED_SANDBOX_ONLY
- `owner_question_if_any`: Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?
- `notes`: Version drift remains possible across hosts.

### LANGUAGES_GO — Go

- `capability_id`: LANGUAGES_GO
- `name`: Go
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: Go: Mass intake candidate for Go in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-go
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; languages-go_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### LANGUAGES_HTML_CSS — HTML/CSS

- `capability_id`: LANGUAGES_HTML_CSS
- `name`: HTML/CSS
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: HTML/CSS: Mass intake candidate for HTML/CSS in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-html-css
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; languages-html-css_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### LANGUAGES_JAVASCRIPT — JavaScript

- `capability_id`: LANGUAGES_JAVASCRIPT
- `name`: JavaScript
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: JavaScript: Mass intake candidate for JavaScript in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-javascript
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; languages-javascript_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### LANGUAGES_POWERSHELL — PowerShell

- `capability_id`: LANGUAGES_POWERSHELL
- `name`: PowerShell
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: PowerShell: Mass intake candidate for PowerShell in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-powershell
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; languages-powershell_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### LANGUAGES_PYTHON_312_RUNTIME — Python 3.12 runtime

- `capability_id`: LANGUAGES_PYTHON_312_RUNTIME
- `name`: Python 3.12 runtime
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: Python 3.12 runtime: Mass intake candidate for Python 3.12 runtime in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-python-312-runtime
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; languages-python-312-runtime_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### LANGUAGES_RUST — Rust

- `capability_id`: LANGUAGES_RUST
- `name`: Rust
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: Rust: Mass intake candidate for Rust in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-rust
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; languages-rust_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### LANGUAGES_SQL — SQL

- `capability_id`: LANGUAGES_SQL
- `name`: SQL
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: SQL: Mass intake candidate for SQL in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-sql
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; languages-sql_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### LANGUAGES_TYPESCRIPT — TypeScript

- `capability_id`: LANGUAGES_TYPESCRIPT
- `name`: TypeScript
- `category`: LANGUAGES
- `status`: CANDIDATE
- `plain_ru_description`: TypeScript: Mass intake candidate for TypeScript in LANGUAGES.
- `why_needed_for_imperium`: Mass intake seed for LANGUAGES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:languages-typescript
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; languages-typescript_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.
