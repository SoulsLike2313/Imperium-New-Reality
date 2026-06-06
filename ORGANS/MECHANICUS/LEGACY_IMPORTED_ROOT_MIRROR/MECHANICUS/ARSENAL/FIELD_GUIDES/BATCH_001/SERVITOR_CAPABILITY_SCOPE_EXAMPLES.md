# Servitor Capability Scope Examples

## visual_dashboard_task

- allowed CANON/SANDBOX capabilities:
  - CAP-LANG-PYTHON312-RUNTIME, CAP-TOOL-COMMAND-GATEWAY-INTERNAL, CAP-TOOL-PATH-POLICY-INTERNAL, CAP-TOOL-RECEIPT-MODELS-VALIDATORS
- candidate-only capabilities:
  - LANGUAGES_GO, LANGUAGES_HTML_CSS, LANGUAGES_JAVASCRIPT, LANGUAGES_POWERSHELL, LANGUAGES_PYTHON_312_RUNTIME, LANGUAGES_RUST, LANGUAGES_SQL, LANGUAGES_TYPESCRIPT
- forbidden capabilities:
  - -
- required receipts:
  - cap-lang-python312-runtime_receipt.json, cap-tool-command-gateway-internal_receipt.json, src/imperium/security/command_gateway.py, src/imperium/security/__init__.py, cap-tool-path-policy-internal_receipt.json, src/imperium/security/path_policy.py, cap-tool-receipt-models-validators_receipt.json, src/imperium/receipts/model.py, src/imperium/receipts/validator.py, src/imperium/receipts/__init__.py
- Owner questions:
  - LANGUAGES_GO: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | LANGUAGES_JAVASCRIPT: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | LANGUAGES_PYTHON_312_RUNTIME: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | LANGUAGES_RUST: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | LANGUAGES_TYPESCRIPT: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?

## code_quality_task

- allowed CANON/SANDBOX capabilities:
  - CAP-LANG-PYTHON312-RUNTIME, CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE, CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT, CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE, CAP-TOOL-COMMAND-GATEWAY-INTERNAL, CAP-TOOL-PATH-POLICY-INTERNAL, CAP-TOOL-RECEIPT-MODELS-VALIDATORS
- candidate-only capabilities:
  - CAP-CQ-PRECOMMIT, CAP-CQ-PYRIGHT-MYPY, CAP-CQ-RUFF, CODE_QUALITY_JSONSCHEMA, CODE_QUALITY_MYPY, CODE_QUALITY_PRE_COMMIT, CODE_QUALITY_PYRIGHT, CODE_QUALITY_PYTEST
- forbidden capabilities:
  - -
- required receipts:
  - cap-lang-python312-runtime_receipt.json, cap-playbook-mechanicus-arsenal-intake_receipt.json, cap-playbook-schema-first-contract_receipt.json, IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json, IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json, cap-playbook-visual-screenshot-gate_receipt.json, cap-tool-command-gateway-internal_receipt.json, src/imperium/security/command_gateway.py, src/imperium/security/__init__.py, cap-tool-path-policy-internal_receipt.json, src/imperium/security/path_policy.py, cap-tool-receipt-models-validators_receipt.json
- Owner questions:
  - CAP-CQ-PRECOMMIT: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CAP-CQ-PYRIGHT-MYPY: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CAP-CQ-RUFF: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CODE_QUALITY_JSONSCHEMA: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CODE_QUALITY_MYPY: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CODE_QUALITY_PRE_COMMIT: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?

## evidence_index_task

- allowed CANON/SANDBOX capabilities:
  - CAP-REF-PATHLIB-DISCIPLINE, CAP-TOOL-COMMAND-GATEWAY-INTERNAL, CAP-TOOL-PATH-POLICY-INTERNAL, CAP-TOOL-RECEIPT-MODELS-VALIDATORS
- candidate-only capabilities:
  - CAP-DB-SQLITE-FTS5-EVIDENCE, DATABASES_CAPABILITY_REGISTRY_DATABASE, DATABASES_CSV_AUDIT_TABLE, DATABASES_DUCKDB, DATABASES_GRAPH_EDGE_LIST, DATABASES_JSONL_EVIDENCE_STREAM, DATABASES_SQLITE, DATABASES_SQLITE_FTS5
- forbidden capabilities:
  - -
- required receipts:
  - cap-ref-pathlib-discipline_receipt.json, cap-tool-command-gateway-internal_receipt.json, src/imperium/security/command_gateway.py, src/imperium/security/__init__.py, cap-tool-path-policy-internal_receipt.json, src/imperium/security/path_policy.py, cap-tool-receipt-models-validators_receipt.json, src/imperium/receipts/model.py, src/imperium/receipts/validator.py, src/imperium/receipts/__init__.py
- Owner questions:
  - CAP-DB-SQLITE-FTS5-EVIDENCE: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | DATABASES_CAPABILITY_REGISTRY_DATABASE: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | DATABASES_CSV_AUDIT_TABLE: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | DATABASES_DUCKDB: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | DATABASES_GRAPH_EDGE_LIST: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | DATABASES_JSONL_EVIDENCE_STREAM: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?

## repo_hygiene_task

- allowed CANON/SANDBOX capabilities:
  - CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE, CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT, CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE, CAP-TOOL-COMMAND-GATEWAY-INTERNAL, CAP-TOOL-PATH-POLICY-INTERNAL, CAP-TOOL-RECEIPT-MODELS-VALIDATORS, CAP-UTILITY-GIT, CAP-UTILITY-POWERSHELL
- candidate-only capabilities:
  - ALGORITHMS_CAPABILITY_PROMOTION_RULES, ALGORITHMS_DIFF_CLASSIFIER, ALGORITHMS_DIRTY_TREE_CLASSIFIER, ALGORITHMS_EVIDENCE_RANKING, ALGORITHMS_FAKE_GREEN_DETECTOR, ALGORITHMS_OWNER_QUESTION_CLASSIFIER, ALGORITHMS_RUNTIME_JUNK_CLASSIFIER, ALGORITHMS_TASK_SCOPE_SPLITTER
- forbidden capabilities:
  - -
- required receipts:
  - cap-playbook-mechanicus-arsenal-intake_receipt.json, cap-playbook-schema-first-contract_receipt.json, IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json, IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json, cap-playbook-visual-screenshot-gate_receipt.json, cap-tool-command-gateway-internal_receipt.json, src/imperium/security/command_gateway.py, src/imperium/security/__init__.py, cap-tool-path-policy-internal_receipt.json, src/imperium/security/path_policy.py, cap-tool-receipt-models-validators_receipt.json, src/imperium/receipts/model.py
- Owner questions:
  - -

## taskpack_generation_task

- allowed CANON/SANDBOX capabilities:
  - CAP-EXAMPLE-LOCAL-HTTP-DASHBOARD-SERVER, CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE, CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT, CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE, CAP-REF-PATHLIB-DISCIPLINE, CAP-TOOL-COMMAND-GATEWAY-INTERNAL, CAP-TOOL-PATH-POLICY-INTERNAL, CAP-TOOL-RECEIPT-MODELS-VALIDATORS
- candidate-only capabilities:
  - EXAMPLES_CAPABILITY_SCOPE_EXAMPLE, EXAMPLES_EVIDENCE_REPORT_EXAMPLE, EXAMPLES_INQUISITION_HYGIENE_SCAN_EXAMPLE, EXAMPLES_MECHANICUS_TOOL_INTAKE_EXAMPLE, EXAMPLES_ORGAN_CONSOLE_EXAMPLE, EXAMPLES_OWNER_DECISION_QUEUE_EXAMPLE, EXAMPLES_TASKPACK_EXAMPLE, EXAMPLES_VISUAL_GATE_EXAMPLE
- forbidden capabilities:
  - -
- required receipts:
  - cap-example-local-http-dashboard-server_receipt.json, cap-playbook-mechanicus-arsenal-intake_receipt.json, cap-playbook-schema-first-contract_receipt.json, IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json, IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json, cap-playbook-visual-screenshot-gate_receipt.json, cap-ref-pathlib-discipline_receipt.json, cap-tool-command-gateway-internal_receipt.json, src/imperium/security/command_gateway.py, src/imperium/security/__init__.py, cap-tool-path-policy-internal_receipt.json, src/imperium/security/path_policy.py
- Owner questions:
  - -

## mechanicus_tool_validation_task

- allowed CANON/SANDBOX capabilities:
  - CAP-TOOL-COMMAND-GATEWAY-INTERNAL, CAP-TOOL-PATH-POLICY-INTERNAL, CAP-TOOL-RECEIPT-MODELS-VALIDATORS, CAP-UTILITY-GIT, CAP-UTILITY-POWERSHELL
- candidate-only capabilities:
  - CAP-CQ-PRECOMMIT, CAP-CQ-PYRIGHT-MYPY, CAP-CQ-RUFF, CODE_QUALITY_JSONSCHEMA, CODE_QUALITY_MYPY, CODE_QUALITY_PRE_COMMIT, CODE_QUALITY_PYRIGHT, CODE_QUALITY_PYTEST
- forbidden capabilities:
  - -
- required receipts:
  - cap-tool-command-gateway-internal_receipt.json, src/imperium/security/command_gateway.py, src/imperium/security/__init__.py, cap-tool-path-policy-internal_receipt.json, src/imperium/security/path_policy.py, cap-tool-receipt-models-validators_receipt.json, src/imperium/receipts/model.py, src/imperium/receipts/validator.py, src/imperium/receipts/__init__.py, cap-utility-git_receipt.json, cap-utility-powershell_receipt.json
- Owner questions:
  - CAP-CQ-PRECOMMIT: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CAP-CQ-PYRIGHT-MYPY: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CAP-CQ-RUFF: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CODE_QUALITY_JSONSCHEMA: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CODE_QUALITY_MYPY: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом? | CODE_QUALITY_PRE_COMMIT: Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?
