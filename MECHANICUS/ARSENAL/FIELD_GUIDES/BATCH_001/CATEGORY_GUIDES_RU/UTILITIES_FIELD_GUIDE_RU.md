# UTILITIES Field Guide (RU)

## Назначение категории
- System and workflow utility capabilities.

## Сводка
- Всего capability: 10
- CANDIDATE: 8
- SANDBOX: 2
- CANON: 0
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-UTILITY-GIT — git

- `capability_id`: CAP-UTILITY-GIT
- `name`: git
- `category`: UTILITIES
- `status`: SANDBOX
- `plain_ru_description`: git: Repository truth checks and version traceability.
- `why_needed_for_imperium`: Supports clean-state and head-verification gates.
- `servitor_usage`: Разрешено только в sandbox-контуре с явной валидационной receipt.
- `local_agent_usage`: Локальный агент может запускать только в экспериментальном контуре.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-utility-git
- `receipt_gate_needed`: GATE-U00-GIT-TRUTH; cap-utility-git_receipt.json
- `task_scope_export_status`: EXPORT_ALLOWED_SANDBOX_ONLY
- `owner_question_if_any`: Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?
- `notes`: Unsafe operations remain possible without discipline.

### CAP-UTILITY-POWERSHELL — PowerShell

- `capability_id`: CAP-UTILITY-POWERSHELL
- `name`: PowerShell
- `category`: UTILITIES
- `status`: SANDBOX
- `plain_ru_description`: PowerShell: Primary PC executor for bounded automation.
- `why_needed_for_imperium`: Provides deterministic command orchestration.
- `servitor_usage`: Разрешено только в sandbox-контуре с явной валидационной receipt.
- `local_agent_usage`: Локальный агент может запускать только в экспериментальном контуре.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-utility-powershell
- `receipt_gate_needed`: GATE-U21-COMMAND-CHUNKING; cap-utility-powershell_receipt.json
- `task_scope_export_status`: EXPORT_ALLOWED_SANDBOX_ONLY
- `owner_question_if_any`: Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?
- `notes`: Host permissions can expose risky operations.

### UTILITIES_7_ZIP — 7-Zip

- `capability_id`: UTILITIES_7_ZIP
- `name`: 7-Zip
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: 7-Zip: Mass intake candidate for 7-Zip in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-7-zip
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-7-zip_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### UTILITIES_ARCHIVE_MANIFEST_GENERATOR — archive manifest generator

- `capability_id`: UTILITIES_ARCHIVE_MANIFEST_GENERATOR
- `name`: archive manifest generator
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: archive manifest generator: Mass intake candidate for archive manifest generator in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-archive-manifest-generator
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-archive-manifest-generator_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### UTILITIES_FD — fd

- `capability_id`: UTILITIES_FD
- `name`: fd
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: fd: Mass intake candidate for fd in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-fd
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-fd_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### UTILITIES_JQ — jq

- `capability_id`: UTILITIES_JQ
- `name`: jq
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: jq: Mass intake candidate for jq in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-jq
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-jq_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### UTILITIES_RIPGREP — ripgrep

- `capability_id`: UTILITIES_RIPGREP
- `name`: ripgrep
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: ripgrep: Mass intake candidate for ripgrep in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-ripgrep
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-ripgrep_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### UTILITIES_SAFE_DELETE_QUARANTINE_WRAPPER — safe delete/quarantine wrapper

- `capability_id`: UTILITIES_SAFE_DELETE_QUARANTINE_WRAPPER
- `name`: safe delete/quarantine wrapper
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: safe delete/quarantine wrapper: Mass intake candidate for safe delete/quarantine wrapper in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-safe-delete-quarantine-wrapper
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-safe-delete-quarantine-wrapper_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### UTILITIES_SHA256_HASHING — SHA256 hashing

- `capability_id`: UTILITIES_SHA256_HASHING
- `name`: SHA256 hashing
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: SHA256 hashing: Mass intake candidate for SHA256 hashing in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-sha256-hashing
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-sha256-hashing_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### UTILITIES_YQ — yq

- `capability_id`: UTILITIES_YQ
- `name`: yq
- `category`: UTILITIES
- `status`: CANDIDATE
- `plain_ru_description`: yq: Mass intake candidate for yq in UTILITIES.
- `why_needed_for_imperium`: Mass intake seed for UTILITIES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:utilities-yq
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; utilities-yq_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.
