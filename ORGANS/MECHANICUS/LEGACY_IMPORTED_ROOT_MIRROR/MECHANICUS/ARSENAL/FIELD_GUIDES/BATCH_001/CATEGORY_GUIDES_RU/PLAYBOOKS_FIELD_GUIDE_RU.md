# PLAYBOOKS Field Guide (RU)

## Назначение категории
- Operational practices and procedures.

## Сводка
- Всего capability: 12
- CANDIDATE: 9
- SANDBOX: 2
- CANON: 1
- QUARANTINE: 0
- REJECTED: 0

## Capability entries

### CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE — Mechanicus Arsenal card intake practice

- `capability_id`: CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE
- `name`: Mechanicus Arsenal card intake practice
- `category`: PLAYBOOKS
- `status`: SANDBOX
- `plain_ru_description`: Mechanicus Arsenal card intake practice: Controlled intake and triage workflow for capabilities.
- `why_needed_for_imperium`: Prevents unregistered tool adoption and trust drift.
- `servitor_usage`: Разрешено только в sandbox-контуре с явной валидационной receipt.
- `local_agent_usage`: Локальный агент может запускать только в экспериментальном контуре.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-playbook-mechanicus-arsenal-intake
- `receipt_gate_needed`: GATE-ARSENAL-INTAKE-COMPLIANCE; cap-playbook-mechanicus-arsenal-intake_receipt.json
- `task_scope_export_status`: EXPORT_ALLOWED_SANDBOX_ONLY
- `owner_question_if_any`: Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?
- `notes`: Foundation-only until additional receipts accumulate.

### CAP-PLAYBOOK-OSINT-DEEP-RESEARCH — OSINT/deep research practice candidate

- `capability_id`: CAP-PLAYBOOK-OSINT-DEEP-RESEARCH
- `name`: OSINT/deep research practice candidate
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: OSINT/deep research practice candidate: Future controlled research playbook candidate.
- `why_needed_for_imperium`: Could support strategic discovery workflows.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-playbook-osint-deep-research
- `receipt_gate_needed`: GATE-ARSENAL-RESEARCH-POLICY; cap-playbook-osint-deep-research_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: No scraping/automation admitted in foundation scope.

### CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT — schema-first JSON contract practice

- `capability_id`: CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT
- `name`: schema-first JSON contract practice
- `category`: PLAYBOOKS
- `status`: CANON
- `plain_ru_description`: schema-first JSON contract practice: Schema-first rule for critical JSON artifacts.
- `why_needed_for_imperium`: Prevents malformed contracts and report drift.
- `servitor_usage`: Разрешено в bounded-задачах при GATE_ACK и приложенных receipts.
- `local_agent_usage`: Локальный агент может применять в рамках узкого scope и доказуемой трассы.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-playbook-schema-first-contract
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; cap-playbook-schema-first-contract_receipt.json; IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json; IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json
- `task_scope_export_status`: EXPORT_ALLOWED_BOUNDED
- `owner_question_if_any`: -
- `notes`: Coverage quality depends on maintained schema scope.

### CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE — visual screenshot gate practice

- `capability_id`: CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE
- `name`: visual screenshot gate practice
- `category`: PLAYBOOKS
- `status`: SANDBOX
- `plain_ru_description`: visual screenshot gate practice: Link visual verdicts to screenshot/report evidence.
- `why_needed_for_imperium`: Lowers fake-green risk in visual acceptance flows.
- `servitor_usage`: Разрешено только в sandbox-контуре с явной валидационной receipt.
- `local_agent_usage`: Локальный агент может запускать только в экспериментальном контуре.
- `allowed_use`: Bounded task execution under Mechanicus policy; Evidence-backed validation and report generation
- `forbidden_use`: Production-ready claim without receipts; Out-of-scope or unbounded execution
- `validation_needed`: validate:cap-playbook-visual-screenshot-gate
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; cap-playbook-visual-screenshot-gate_receipt.json
- `task_scope_export_status`: EXPORT_ALLOWED_SANDBOX_ONLY
- `owner_question_if_any`: Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?
- `notes`: Current evidence is not full-repo coverage.

### PLAYBOOKS_CANDIDATE_CHECK_PLAYBOOK — candidate check playbook

- `capability_id`: PLAYBOOKS_CANDIDATE_CHECK_PLAYBOOK
- `name`: candidate check playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: candidate check playbook: Mass intake candidate for candidate check playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-candidate-check-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-candidate-check-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### PLAYBOOKS_CLEAN_WORKTREE_PLAYBOOK — clean worktree playbook

- `capability_id`: PLAYBOOKS_CLEAN_WORKTREE_PLAYBOOK
- `name`: clean worktree playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: clean worktree playbook: Mass intake candidate for clean worktree playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-clean-worktree-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-clean-worktree-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### PLAYBOOKS_COMMIT_PUSH_GATE_PLAYBOOK — commit push gate playbook

- `capability_id`: PLAYBOOKS_COMMIT_PUSH_GATE_PLAYBOOK
- `name`: commit push gate playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: commit push gate playbook: Mass intake candidate for commit push gate playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-commit-push-gate-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-commit-push-gate-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### PLAYBOOKS_INQUISITION_HYGIENE_PLAYBOOK — Inquisition hygiene playbook

- `capability_id`: PLAYBOOKS_INQUISITION_HYGIENE_PLAYBOOK
- `name`: Inquisition hygiene playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: Inquisition hygiene playbook: Mass intake candidate for Inquisition hygiene playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-inquisition-hygiene-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-inquisition-hygiene-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### PLAYBOOKS_MECHANICUS_TOOL_INTAKE_PLAYBOOK — Mechanicus tool intake playbook

- `capability_id`: PLAYBOOKS_MECHANICUS_TOOL_INTAKE_PLAYBOOK
- `name`: Mechanicus tool intake playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: Mechanicus tool intake playbook: Mass intake candidate for Mechanicus tool intake playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-mechanicus-tool-intake-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-mechanicus-tool-intake-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### PLAYBOOKS_NO_RUNTIME_JUNK_PLAYBOOK — no runtime junk playbook

- `capability_id`: PLAYBOOKS_NO_RUNTIME_JUNK_PLAYBOOK
- `name`: no runtime junk playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: no runtime junk playbook: Mass intake candidate for no runtime junk playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-no-runtime-junk-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-no-runtime-junk-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### PLAYBOOKS_SCOPE_REVIEW_PLAYBOOK — scope review playbook

- `capability_id`: PLAYBOOKS_SCOPE_REVIEW_PLAYBOOK
- `name`: scope review playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: scope review playbook: Mass intake candidate for scope review playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-scope-review-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-scope-review-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.

### PLAYBOOKS_VISUAL_ANTI_DEFAULT_PLAYBOOK — visual anti-default playbook

- `capability_id`: PLAYBOOKS_VISUAL_ANTI_DEFAULT_PLAYBOOK
- `name`: visual anti-default playbook
- `category`: PLAYBOOKS
- `status`: CANDIDATE
- `plain_ru_description`: visual anti-default playbook: Mass intake candidate for visual anti-default playbook in PLAYBOOKS.
- `why_needed_for_imperium`: Mass intake seed for PLAYBOOKS.
- `servitor_usage`: Можно включать в scope как candidate context, но не активировать без SANDBOX admission.
- `local_agent_usage`: Локальный агент может планировать/документировать, но не исполнять.
- `allowed_use`: Capability cataloging and validation planning; Scoped candidate execution after explicit admission gate
- `forbidden_use`: Claiming CANON without validation receipt evidence; Using capability outside bounded task scope
- `validation_needed`: validate:playbooks-visual-anti-default-playbook
- `receipt_gate_needed`: GATE-U09-NO-FAKE-GREEN; playbooks-visual-anti-default-playbook_validation_receipt.json
- `task_scope_export_status`: EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX
- `owner_question_if_any`: -
- `notes`: Candidate-only until validation receipts and trust checks exist.
