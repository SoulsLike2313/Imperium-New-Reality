# DATABASES Field Guide (RU)

## Назначение категории
- Databases and storage engines.

## Сводка
- Всего capability: 9
- CANDIDATE: 9
- SANDBOX: 0
- CANON: 0
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-DB-SQLITE-FTS5-EVIDENCE — SQLite / FTS5 evidence index candidate

- `capability_id`: CAP-DB-SQLITE-FTS5-EVIDENCE
- `name`: SQLite / FTS5 evidence index candidate
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: SQLite / FTS5 evidence index candidate: Candidate local evidence indexing substrate.
- `why_needed_for_imperium`: Could support searchable receipt/report corpus.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-db-sqlite-fts5-evidence
- `receipt_gate_needed`: GATE-ARSENAL-DB-ADMISSION; cap-db-sqlite-fts5-evidence_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: No provisioning or validation in this task.

### DATABASES_CAPABILITY_REGISTRY_DATABASE — capability registry database

- `capability_id`: DATABASES_CAPABILITY_REGISTRY_DATABASE
- `name`: capability registry database
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: capability registry database: Mass intake candidate for capability registry database in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-capability-registry-database
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; databases-capability-registry-database_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### DATABASES_CSV_AUDIT_TABLE — CSV audit table

- `capability_id`: DATABASES_CSV_AUDIT_TABLE
- `name`: CSV audit table
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: CSV audit table: Mass intake candidate for CSV audit table in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-csv-audit-table
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; databases-csv-audit-table_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### DATABASES_DUCKDB — DuckDB

- `capability_id`: DATABASES_DUCKDB
- `name`: DuckDB
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: DuckDB: Mass intake candidate for DuckDB in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-duckdb
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; databases-duckdb_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### DATABASES_GRAPH_EDGE_LIST — graph edge list

- `capability_id`: DATABASES_GRAPH_EDGE_LIST
- `name`: graph edge list
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: graph edge list: Mass intake candidate for graph edge list in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-graph-edge-list
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; databases-graph-edge-list_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### DATABASES_JSONL_EVIDENCE_STREAM — JSONL evidence stream

- `capability_id`: DATABASES_JSONL_EVIDENCE_STREAM
- `name`: JSONL evidence stream
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: JSONL evidence stream: Mass intake candidate for JSONL evidence stream in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-jsonl-evidence-stream
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; databases-jsonl-evidence-stream_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.

### DATABASES_SQLITE — SQLite

- `capability_id`: DATABASES_SQLITE
- `name`: SQLite
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: SQLite: Mass intake candidate for SQLite in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-sqlite
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; databases-sqlite_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### DATABASES_SQLITE_FTS5 — SQLite FTS5

- `capability_id`: DATABASES_SQLITE_FTS5
- `name`: SQLite FTS5
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: SQLite FTS5: Mass intake candidate for SQLite FTS5 in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-sqlite-fts5
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; databases-sqlite-fts5_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### DATABASES_TASK_EVIDENCE_STORE — task evidence store

- `capability_id`: DATABASES_TASK_EVIDENCE_STORE
- `name`: task evidence store
- `category`: DATABASES
- `status`: CANDIDATE
- `plain_ru_description`: task evidence store: Mass intake candidate for task evidence store in DATABASES.
- `why_needed_for_imperium`: Mass intake seed for DATABASES.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:databases-task-evidence-store
- `receipt_gate_needed`: GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION; databases-task-evidence-store_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
- `notes`: Candidate-only until validation receipts and trust checks exist.
