# Tool Decision Matrix RU — TASK-NEWGEN-MECHANICUS-TOOLS-EXPANSION-BATCH-PC-V0_1

| Tool ID | Группа | Present | Текущий статус | Decision | Риск | Плюсы | Минусы |
|---|---|---:|---|---|---|---|---|
| UTILITIES_RIPGREP | SEARCH_CODE_NAVIGATION | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | Fast repo-wide search.; Already used in Mechanicus workflows. | External binary dependency. |
| SEARCH_INDEXING_RIPGREP_SEARCH | SEARCH_CODE_NAVIGATION | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | Gives high-density evidence discovery. | Depends on ripgrep binary availability. |
| UTILITIES_FD | SEARCH_CODE_NAVIGATION | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | Very fast file traversal. | Alternative command names on Windows/Linux. |
| LANGUAGES_POWERSHELL | SEARCH_CODE_NAVIGATION | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Built-in fallback without installs. | Slower than ripgrep for large trees. |
| PYTHON_PATHLIB_GLOB_FALLBACK | SEARCH_CODE_NAVIGATION | yes | NO_CARD | KEEP_CANDIDATE | LOW | No extra install; deterministic fallback. | Slow on deep trees. |
| UTILITIES_JQ | JSON_YAML_DATA | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | Compact JSON filtering in shell lanes. | Extra binary if not preinstalled. |
| UTILITIES_YQ | JSON_YAML_DATA | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | YAML+JSON transformations in one CLI. | Not required for minimal tasks. |
| CAP-TOOL-JSONSCHEMA | JSON_YAML_DATA | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Schema-first guard for machine artifacts. | CLI is deprecated; future migration to check-jsonschema likely. |
| CODE_QUALITY_JSONSCHEMA | JSON_YAML_DATA | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Shared validator across reports/contracts. | Long-term CLI replacement should be planned. |
| REFERENCE_CODE_SAFE_JSON_WRITE_HELPER | JSON_YAML_DATA | yes | CANDIDATE | KEEP_CANDIDATE | LOW | Reduces malformed JSON artifact risk. | Reference pattern, not standalone executable. |
| UTILITIES_7_ZIP | ARCHIVE_HASH_EVIDENCE | no | CANDIDATE | OWNER_APPROVAL_REQUIRED | MEDIUM | Strong archive tooling for taskpack checks. | Not installed on many hosts; install required. |
| TAR_ZIP_RUNTIME_AVAILABILITY | ARCHIVE_HASH_EVIDENCE | yes | NO_CARD | KEEP_CANDIDATE | LOW | Built-in archive fallback without extra install. | tar CLI behavior differs across shells. |
| UTILITIES_ARCHIVE_MANIFEST_GENERATOR | ARCHIVE_HASH_EVIDENCE | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | Supports deterministic hash manifest creation. | Current implementation is fallback, not dedicated CLI. |
| UTILITIES_SHA256_HASHING | ARCHIVE_HASH_EVIDENCE | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | Critical for evidence integrity. | Some environments lack Get-FileHash cmdlet. |
| DATABASES_SQLITE | ARCHIVE_HASH_EVIDENCE | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Core storage for Evidence Index. | Limited by stdlib compile options. |
| DATABASES_SQLITE_FTS5 | ARCHIVE_HASH_EVIDENCE | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Enables fast evidence full-text search. | Fails if Python sqlite build lacks fts5. |
| SEARCH_INDEXING_SQLITE_FTS_SEARCH | ARCHIVE_HASH_EVIDENCE | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Direct query lane for evidence retrieval. | Depends on current index refresh state. |
| CODE_QUALITY_RUFF | REPO_HYGIENE_SAFETY | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Fast lint guard for script quality. | Can block on style drift if run too broad. |
| CODE_QUALITY_MYPY | REPO_HYGIENE_SAFETY | yes | SANDBOX | VALIDATE_IF_PRESENT | LOW | Type-safety evidence for reusable scripts. | First-pass warnings acceptable in this step. |
| ALGORITHMS_RUNTIME_JUNK_CLASSIFIER | REPO_HYGIENE_SAFETY | yes | CANDIDATE | KEEP_CANDIDATE | LOW | Prevents noisy dirty-state from generated artifacts. | Classifier quality depends on maintained ignore rules. |
| TOOLS_SCOPE_REVIEW_TOOL | REPO_HYGIENE_SAFETY | yes | CANDIDATE | INSTALL_OR_VALIDATE_NOW | LOW | Guards fake-CANON and scope mismatch drift. | Needs jsonschema package for full checks. |
| TOOLS_CANDIDATE_CHECK_WORKFLOW | REPO_HYGIENE_SAFETY | yes | CANDIDATE | KEEP_CANDIDATE | LOW | Structured validation-to-receipt flow exists. | Current workflow tuned for earlier batches. |
| TOOLS_TASKPACK_DOSSIER_BUILDER | REPORTING_TASKPACK | yes | CANDIDATE | KEEP_CANDIDATE | LOW | Existing validator supports dossier quality checks. | Dedicated builder tool still candidate-level concept. |
| MARKDOWNLINT_CLI | REPORTING_TASKPACK | no | NO_CARD | OWNER_APPROVAL_REQUIRED | MEDIUM | Automated markdown contract hygiene. | Node-based install; not currently present. |
| CHECK_JSONSCHEMA_CLI | REPORTING_TASKPACK | no | NO_CARD | OWNER_APPROVAL_REQUIRED | MEDIUM | Modern replacement for deprecated jsonschema CLI. | Not installed by default. |
| YAMLLINT_CLI | REPORTING_TASKPACK | no | NO_CARD | OWNER_APPROVAL_REQUIRED | MEDIUM | Strict YAML lint for future taskpack variants. | Not needed for current JSON-first core flows. |
