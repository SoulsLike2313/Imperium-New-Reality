# Owner Decision Points (RU)

## Q-ARS-001 — CODE_QUALITY
- Вопрос: Choose primary type checker lane for Python promotion: pyright-first, mypy-first, or dual-lane?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-002 — VISUAL_TESTING
- Вопрос: Do we prioritize Playwright-only visual baseline first, or multi-runner strategy later?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-003 — DATABASES
- Вопрос: Should SQLite remain default evidence store, or should DuckDB become co-primary?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-004 — UI_FRAMEWORKS
- Вопрос: For owner-facing cockpit work, do we anchor plain HTML/CSS/JS first or React/Vite first?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-005 — CLOUD_LLM_ADAPTERS
- Вопрос: Which secret-policy baseline is required before any cloud adapter leaves CANDIDATE?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-006 — LOCAL_LLM
- Вопрос: Which local runner is the first dedicated validation target (Ollama, llama.cpp, or LM Studio)?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-007 — SEARCH_INDEXING
- Вопрос: Do we prioritize ripgrep-index manifest strategy or a DB-backed index strategy first?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-008 — TOOLS
- Вопрос: Should external tool admissions happen by category waves or by dependency chains?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-009 — PROMPTING_PATTERNS
- Вопрос: Do we canonize any prompt patterns early, or keep all prompting cards candidate until audit cycle?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-ARS-010 — PLAYBOOKS
- Вопрос: Which playbook should be promoted first as cross-organ standard: scope-review or no-fake-green?
- Рекомендация: Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.

## Q-FG-011 — STATUS_PROMOTION_POLICY
- Вопрос: Подтвердить единые критерии SANDBOX -> CANON для всех категорий (минимальный набор receipts и checks).
- Рекомендация: Утвердить canonical receipt baseline и gate checklist.

## Q-FG-012 — INSTALL_ADMISSION_WAVES
- Вопрос: Какой порядок installation-admission предпочтителен: волнами по категориям или по dependency-цепочкам?
- Рекомендация: Начать с P0/P1 и переходить к P2/P3 после подтверждения стабильности.
