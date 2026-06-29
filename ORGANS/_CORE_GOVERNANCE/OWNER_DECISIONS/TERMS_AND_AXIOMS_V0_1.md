# TERMS_AND_AXIOMS_V0_1

Status: `OWNER_LOCKED_PROSE`
Admission: `DIRECT_REALITY_BY_OWNER`
Pack: `IMPERIUM-OWNER-FOUNDATION-DOCS-REALITY-0001`
Generated UTC: `2026-06-29T08:07:47.533447+00:00`
Validation: `PENDING_WARP_VALIDATORS`

## 1. Главные термины

### Owner

Суверенный источник воли, решений, override и конечного review.

### Logos Prime

Governance/membrane-роль LLM-присутствия, переводящая волю Owner-а в инженерную форму: документы, матрицы, схемы, валидаторы, receipts, roadmap, вопросы и доказательства. Logos Prime не является органом и не подменяет Owner-а.

### Throne / Трон

Коронный орган. Держит форму ядра, валидирует 9 органов, проверяет trust evidence, считает разрыв между declared и actual, защищает CORE/HARNESS/WARP/Reality границы и выдаёт финальный verdict.

### Great Nine / Великая 9ка

Девять рабочих органов Империума:

```text
ASTRONOMICON
ADMINISTRATUM
DOCTRINARIUM
MECHANICUS
INQUISITION
CUSTODES
STRATEGIUM
SCHOLA_IMPERIALIS
OFFICIO_AGENTIS
```

### Organ slots / органные слоты

Обязательные полости органа: единый внешний интерфейс, который позволяет проверять разные органы одинаковым способом.

### Unique organ extension / уникальное расширение органа

Дополнительный слот сверх общего стандарта. Разрешён только при декларации в паспорте/manifest и прохождении validator-а.

### Population / население Империума

Всё, что живёт внутри контролируемых территорий: файлы, каталоги, органы, формы, tools, validators, schemas, matrices, receipts, reports, roles, servitors, WARP artifacts, garbage, quarantine, negative examples, archives.

### Imperium ID

Уникальный идентификатор каждого жителя Империума. Нужен для provenance, владения, validation history и clean-up.

### Task pack

Задача для сервитора / кодового исполнителя. Содержит task_id, micro_prompt, context request, pass criteria, expected receipts, execution boundaries и fix-loop policy.

### Patch pack

Ручная/chat-agent delta, которую Owner и Logos Prime собирают в диалоге. Внедряется руками или через контролируемый patch-процесс. Может быть не задачей для CLI-сервитора.

### WARP

Зона изменяемой работы, эксперимента, проверки и abort/land выбора. Любое изменение сначала должно быть доказано в WARP, кроме прямых owner-foundation documents, явно разрешённых к Reality.

### Reality

Активная реальность репозитория. То, что считается current truth после admission/land.

### Receipt

Доказательство проверки. Без receipt PASS не признаётся честным.

### Verdict

Решение gate/validator/organ/Throne: PASS, WARN, WARP_ONLY, BLOCK_LAND, BLOCK_CYCLE или иной явно заявленный статус.

### Declared vs Actual Gap

Разрыв между тем, что документ/орган заявляет, и тем, что фактически найдено в файловой системе и проверках. На ранних этапах не блокирует, а даёт карту развития.

### Core Leveling

Система роста ядра до версии 1.0 через метрики полноты, валидации, receipts, доверия, видимости, backup и mutation guard.

---

## 2. Аксиомы

### AXIOM-001 — Owner sovereignty

Финальный override принадлежит только Owner-у.

### AXIOM-002 — No fake green

PASS без receipt, validation evidence и текущей правды считается fake-green.

### AXIOM-003 — Rule births validator

Родилось правило → должен родиться validator.

### AXIOM-004 — Form births schema

Родилась форма → должна родиться schema.

### AXIOM-005 — Validator births receipt

Родился validator → должен рождать receipt.

### AXIOM-006 — Receipt requires registration

Receipt без регистрации в Administratum не является полноценным доказательством.

### AXIOM-007 — Throne requires Nine

Трон не имеет права заявить полноту ядра без 9 органов.

### AXIOM-008 — Nine require Throne

9 органов не являются защищённым самоописанным ядром без Трона.

### AXIOM-009 — Core completeness is multiplicative

```text
CORE_COMPLETENESS = THRONE_COMPLETENESS × GREAT_NINE_COMPLETENESS
```

### AXIOM-010 — Documents are not execution

Документ задаёт форму, но не доказывает исполнение без validator-а и receipt.

### AXIOM-011 — Validators outrank prose

В споре между красивым описанием и строгим validator-ом приоритет имеет validator.

### AXIOM-012 — Gaps are fuel

Разрыв declared vs actual — не позор, а топливо для roadmap и leveling.

### AXIOM-013 — Inquisition detects dust

Инквизиция обязана ловить даже малую грязь, если она может помешать работе.

### AXIOM-014 — WARP-first work

Будущие изменения проходят через WARP, пока Owner не дал явное решение land/abort.

### AXIOM-015 — Visual refit frozen

Eyes/Graph visual refit заморожен. Разрешены только data exports/status feeds для стабильной принятой точки.
