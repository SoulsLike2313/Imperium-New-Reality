# Validation Priority Queue (RU)

Целевая задача: `TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1`

## P0_EXISTING_INTERNAL_CAPABILITIES

- Всего: 6

- CAP-LANG-PYTHON312-RUNTIME (LANGUAGES, SANDBOX, SANDBOX_ONLY): Internal/built-in capability; fastest to re-validate with low dependency risk.
- CAP-TOOL-COMMAND-GATEWAY-INTERNAL (TOOLS, CANON, CANON_ALLOWED): Internal/built-in capability; fastest to re-validate with low dependency risk.
- CAP-TOOL-PATH-POLICY-INTERNAL (TOOLS, CANON, CANON_ALLOWED): Internal/built-in capability; fastest to re-validate with low dependency risk.
- CAP-TOOL-RECEIPT-MODELS-VALIDATORS (TOOLS, CANON, CANON_ALLOWED): Internal/built-in capability; fastest to re-validate with low dependency risk.
- CAP-UTILITY-GIT (UTILITIES, SANDBOX, SANDBOX_ONLY): Internal/built-in capability; fastest to re-validate with low dependency risk.
- CAP-UTILITY-POWERSHELL (UTILITIES, SANDBOX, SANDBOX_ONLY): Internal/built-in capability; fastest to re-validate with low dependency risk.

## P1_CORE_DEV_TOOLS

- Всего: 30

- CAP-CQ-PRECOMMIT (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CAP-CQ-PYRIGHT-MYPY (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CAP-CQ-RUFF (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_JSONSCHEMA (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_MYPY (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_PRE_COMMIT (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_PYRIGHT (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_PYTEST (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_PY_COMPILE (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_RUFF (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CODE_QUALITY_SCHEMA_FIRST_VALIDATION (CODE_QUALITY, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_GO (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_HTML_CSS (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_JAVASCRIPT (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_POWERSHELL (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_PYTHON_312_RUNTIME (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_RUST (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_SQL (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- LANGUAGES_TYPESCRIPT (LANGUAGES, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CAP-TOOL-JSONSCHEMA (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CAP-TOOL-NODE-NPM-NPX (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- CAP-TOOL-PYTEST (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_CANDIDATE_CHECK_WORKFLOW (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_COMMAND_GATEWAY (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_COMMIT_PUSH_WORKFLOW (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_GIT (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_PATH_POLICY (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_RECEIPT_VALIDATOR (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_SCOPE_REVIEW_TOOL (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.
- TOOLS_TASKPACK_DOSSIER_BUILDER (TOOLS, CANDIDATE, TASK_SCOPE_ALLOWED): Core developer workflow capability; high leverage for quality and discipline.

## P2_VISUAL_UI_TOOLS

- Всего: 17

- UI_FRAMEWORKS_FRAMER_MOTION (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- UI_FRAMEWORKS_LUCIDE_ICONS (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- UI_FRAMEWORKS_PLAIN_HTML_CSS_JS_COCKPIT (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- UI_FRAMEWORKS_REACT (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- UI_FRAMEWORKS_RECHARTS (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- UI_FRAMEWORKS_SHADCN_UI (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- UI_FRAMEWORKS_TAILWIND_CSS (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- UI_FRAMEWORKS_VITE (UI_FRAMEWORKS, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- CAP-VIS-PLAYWRIGHT-REGRESSION (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_ANTI_GENERIC_ADMIN_VISUAL_GATE (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_PLAYWRIGHT (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_RESPONSIVE_VIEWPORT_CHECKLIST (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_SCREENSHOT_BASELINE_PRACTICE (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_SCREENSHOT_MANIFEST (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_STATIC_HTML_VISUAL_CHECK (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_VISUAL_EVIDENCE_REPORT (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.
- VISUAL_TESTING_VISUAL_LAYOUT_CONTRACT (VISUAL_TESTING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed for dashboard/visual corridor but still candidate-heavy.

## P3_EVIDENCE_SEARCH_TOOLS

- Всего: 26

- CAP-DB-SQLITE-FTS5-EVIDENCE (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_CAPABILITY_REGISTRY_DATABASE (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_CSV_AUDIT_TABLE (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_DUCKDB (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_GRAPH_EDGE_LIST (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_JSONL_EVIDENCE_STREAM (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_SQLITE (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_SQLITE_FTS5 (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- DATABASES_TASK_EVIDENCE_STORE (DATABASES, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- CAP-REF-PATHLIB-DISCIPLINE (REFERENCE_CODE, SANDBOX, SANDBOX_ONLY): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_CAPABILITY_CARD_SCHEMA (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_ORGAN_CONSOLE_LAYOUT_REFERENCE (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_OWNER_QUESTION_SCHEMA (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_READ_ONLY_SMOKE_HARNESS (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_SAFE_JSON_WRITE_HELPER (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_SCOPE_EXPORT_SCHEMA (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_STATUS_BADGE_SYSTEM (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- REFERENCE_CODE_VALIDATION_RECEIPT_SCHEMA (REFERENCE_CODE, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_CATEGORY_LOOKUP_INDEX (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_FUTURE_EMBEDDING_INDEX_PLACEHOLDER (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_RECEIPT_PATH_INDEX (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_REPORT_PATH_INDEX (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_RIPGREP_SEARCH (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_SIMPLE_INVERTED_INDEX (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_SQLITE_FTS_SEARCH (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.
- SEARCH_INDEXING_TAG_INDEX_MODEL (SEARCH_INDEXING, CANDIDATE, TASK_SCOPE_ALLOWED): Needed to improve evidence retrieval/index quality.

## P4_OPERATIONAL_UTILITIES

- Всего: 45

- ALGORITHMS_CAPABILITY_PROMOTION_RULES (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- ALGORITHMS_DIFF_CLASSIFIER (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- ALGORITHMS_DIRTY_TREE_CLASSIFIER (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- ALGORITHMS_EVIDENCE_RANKING (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- ALGORITHMS_FAKE_GREEN_DETECTOR (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- ALGORITHMS_OWNER_QUESTION_CLASSIFIER (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- ALGORITHMS_RUNTIME_JUNK_CLASSIFIER (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- ALGORITHMS_TASK_SCOPE_SPLITTER (ALGORITHMS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- CAP-EXAMPLE-LOCAL-HTTP-DASHBOARD-SERVER (EXAMPLES, SANDBOX, SANDBOX_ONLY): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_CAPABILITY_SCOPE_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_EVIDENCE_REPORT_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_INQUISITION_HYGIENE_SCAN_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_MECHANICUS_TOOL_INTAKE_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_ORGAN_CONSOLE_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_OWNER_DECISION_QUEUE_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_TASKPACK_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- EXAMPLES_VISUAL_GATE_EXAMPLE (EXAMPLES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE (PLAYBOOKS, SANDBOX, SANDBOX_ONLY): Operational support layer that can progress after core lanes stabilize.
- CAP-PLAYBOOK-OSINT-DEEP-RESEARCH (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT (PLAYBOOKS, CANON, CANON_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE (PLAYBOOKS, SANDBOX, SANDBOX_ONLY): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_CANDIDATE_CHECK_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_CLEAN_WORKTREE_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_COMMIT_PUSH_GATE_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_INQUISITION_HYGIENE_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_MECHANICUS_TOOL_INTAKE_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_NO_RUNTIME_JUNK_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_SCOPE_REVIEW_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PLAYBOOKS_VISUAL_ANTI_DEFAULT_PLAYBOOK (PLAYBOOKS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_4_PART_OWNER_REPORT_PROMPT (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_NO_FAKE_GREEN_RESPONSE_PATTERN (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_OWNER_DECISION_QUEUE_PROMPT (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_READ_FIRST_GATE_PROMPT (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_SERVITOR_ROLE_RE_ANCHOR_PROMPT (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_STRUCTURED_ZIP_DOSSIER_PROMPT (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_TASK_CONTINUATION_PROMPT (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- PROMPTING_PATTERNS_VOLUME_BUDGET_PROMPT (PROMPTING_PATTERNS, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_7_ZIP (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_ARCHIVE_MANIFEST_GENERATOR (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_FD (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_JQ (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_RIPGREP (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_SAFE_DELETE_QUARANTINE_WRAPPER (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_SHA256_HASHING (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.
- UTILITIES_YQ (UTILITIES, CANDIDATE, TASK_SCOPE_ALLOWED): Operational support layer that can progress after core lanes stabilize.

## P5_RESERVED_LLM_CLOUD_DEFERRED

- Всего: 12

- CLOUD_LLM_ADAPTERS_CLOUD_MODEL_ROUTER_RESERVED (CLOUD_LLM_ADAPTERS, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- CLOUD_LLM_ADAPTERS_CLOUD_RECEIPT_MODEL_CANDIDATE (CLOUD_LLM_ADAPTERS, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- CLOUD_LLM_ADAPTERS_COST_POLICY_GATE (CLOUD_LLM_ADAPTERS, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- CLOUD_LLM_ADAPTERS_OPENAI_COMPATIBLE_API_ADAPTER_RESERVED (CLOUD_LLM_ADAPTERS, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- CLOUD_LLM_ADAPTERS_PRIVACY_POLICY_GATE (CLOUD_LLM_ADAPTERS, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- CLOUD_LLM_ADAPTERS_SECRET_POLICY_GATE (CLOUD_LLM_ADAPTERS, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- LOCAL_LLM_LLAMACPP_RESERVED_CANDIDATE (LOCAL_LLM, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- LOCAL_LLM_LM_STUDIO_RESERVED_CANDIDATE (LOCAL_LLM, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- LOCAL_LLM_LOCAL_MODEL_RUNNER_RESERVED (LOCAL_LLM, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- LOCAL_LLM_MODEL_CAPABILITY_CARD_PATTERN (LOCAL_LLM, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- LOCAL_LLM_OLLAMA_RESERVED_CANDIDATE (LOCAL_LLM, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
- LOCAL_LLM_OPENAI_COMPATIBLE_LOCAL_ENDPOINT_PATTERN (LOCAL_LLM, CANDIDATE, OWNER_DECISION_REQUIRED): Reserved lane; requires dedicated policy and Owner gate.
