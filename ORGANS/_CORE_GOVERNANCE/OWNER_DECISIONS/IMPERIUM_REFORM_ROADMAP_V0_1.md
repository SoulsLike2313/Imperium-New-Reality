# IMPERIUM_REFORM_ROADMAP_V0_1

Status: `OWNER_LOCKED_PROSE`
Admission: `DIRECT_REALITY_BY_OWNER`
Pack: `IMPERIUM-OWNER-FOUNDATION-DOCS-REALITY-0001`
Generated UTC: `2026-06-29T08:07:47.533447+00:00`
Validation: `PENDING_WARP_VALIDATORS`

## 0. Назначение

Этот roadmap задаёт последовательность внедрения формы Империума. Цель — не расширять хаос, а построить проверяемую систему, где документы, формы, матрицы, валидаторы, receipts, TUI и backup работают как связанный механизм.

Каждая зона должна давать видимую пользу сразу и рождать валидируемые результаты.

## 1. Общая последовательность

```text
ZONE_0  Owner Answer Lock / Terms
ZONE_1  Population Census
ZONE_2  Throne Crown Organ Foundation
ZONE_3  Work Cycle Foundation
ZONE_4  Organ Passport Standard
ZONE_5  Great Nine Passport Stamp
ZONE_6  Custodes Trust Layer
ZONE_7  KPD / Pipeline Validation / Core Leveling
ZONE_8  TUI / Dashboard / Prediction Box
ZONE_9  Enforcement / Backup / Archive Compression
```

---

## ZONE_0 — Owner Answer Lock / Terms

Цель: закрепить решения Owner-а, словарь, базовые аксиомы, режимы, land policy и границы будущей реформы.

Текущий этап.

Outputs:

```text
OWNER_ANSWER_LOCK_V0_1.md
TERMS_AND_AXIOMS_V0_1.md
IMPERIUM_REFORM_ROADMAP_V0_1.md
THRONE_CROWN_ORGAN_DECISION_V0_1.md
OWNER_LAND_POLICY_V0_1.md
VALIDATION_BACKLOG_V0_1.md
```

Видимая польза: появляется фиксированная карта решений, от которой можно строить валидаторы.

---

## ZONE_1 — Population Census

Цель: переписать всё население Империума.

Считать нужно всё: файлы, каталоги, органы, формы, tools, schemas, validators, matrices, receipts, reports, roles, servitors, task packs, patch packs, WARP artifacts, garbage, quarantine, archives.

Минимальные outputs:

```text
IMPERIUM_POPULATION_CENSUS_V0_1.json
IMPERIUM_POPULATION_CENSUS_REPORT_V0_1.md
population_census.schema.json
population_census_validator.py
population_census_receipt.json
```

Видимая польза: Империум впервые знает, кто в нём живёт, кто без владельца, кто мусор, кто в WARP, кто в Reality, кто orphan.

---

## ZONE_2 — Throne Crown Organ Foundation

Цель: сделать Трон реальным коронным органом.

Форма:

```text
ORGANS/THRONE/README.md
ORGANS/THRONE/ORGAN_CARD.json
ORGANS/THRONE/MANIFEST.json
ORGANS/THRONE/FUNCTIONS.md
ORGANS/THRONE/SELF_KNOWLEDGE/
ORGANS/THRONE/MATRICES/
ORGANS/THRONE/SCHEMAS/
ORGANS/THRONE/VALIDATORS/
ORGANS/THRONE/RECEIPTS/
ORGANS/THRONE/TUI/
ORGANS/THRONE/DASHBOARDS/
ORGANS/THRONE/EYES/
```

Видимая польза: Трон перестаёт быть идеей и становится проверяемым коронным органом.

---

## ZONE_3 — Work Cycle Foundation

Цель: закрепить task pack, patch pack, WARP-first cycle, fix loops, land/abort и evidence chain.

Минимальные outputs:

```text
TASK_PACK_FORM_V0_1.md
PATCH_PACK_FORM_V0_1.md
WARP_WORK_CYCLE_V0_1.md
task_pack.schema.json
patch_pack.schema.json
work_cycle_validator.py
pipeline_receipt.schema.json
```

Видимая польза: будущие работы перестают быть разрозненными. Каждый шаг становится проверяемым.

---

## ZONE_4 — Organ Passport Standard

Цель: определить общую форму органа.

Минимальные outputs:

```text
ORGAN_SLOT_MATRIX_V0_1.json
ORGAN_README_TEMPLATE_V0_1.md
ORGAN_CARD.schema.json
ORGAN_MANIFEST.schema.json
organ_passport_validator.py
organ_passport_receipt.schema.json
```

Видимая польза: любой орган можно проверить одинаково, а уникальные расширения становятся контролируемыми.

---

## ZONE_5 — Great Nine Passport Stamp

Цель: паспортизировать 9 органов по единой форме.

Порядок:

```text
1. ASTRONOMICON
2. ADMINISTRATUM
3. DOCTRINARIUM
4. MECHANICUS
5. INQUISITION
6. CUSTODES
7. STRATEGIUM
8. SCHOLA_IMPERIALIS
9. OFFICIO_AGENTIS
```

Видимая польза: появляется таблица органной полноты, declared vs actual gaps и organ leveling.

---

## ZONE_6 — Custodes Trust Layer

Цель: сделать Custodes прослойкой доверия к органам.

Custodes проверяет:

```text
валидаторы органов
receipts органов
органные verdicts
соответствие роли органа
качество доказательств
trust packs
```

Минимальные outputs:

```text
CUSTODES_TRUST_MATRIX_V0_1.json
organ_trust_receipt.schema.json
validate_organ_trust.py
custodes_trust_pack_builder.py
```

Видимая польза: Трон получает не просто органные слова, а пакет доказательства, можно ли органам верить.

---

## ZONE_7 — KPD / Pipeline Validation / Core Leveling

Цель: сделать числа, которым можно верить.

Метрики:

```text
completeness_score
reality_readiness_score
kpd_score
mutation_risk_score
schema_coverage_score
validator_coverage_score
receipt_coverage_score
declared_vs_actual_gap
pipeline_pass_score
trust_score
hardcode_risk_score
warp_debt_score
archive_health_score
backup_readiness_score
```

Видимая польза: цифры начинают рекомендовать области внимания.

---

## ZONE_8 — TUI / Dashboard / Prediction Box

Цель: сделать видимость и управление.

Направление:

```text
Imperium TUI
  → Throne view
  → organ views
  → task execution view
  → receipt/export/archive view
```

Prediction Box должен показывать, как включение/отключение функций меняет возможности Империума, риски, КPD и нагрузку.

Видимая польза: Owner видит состояние системы, а не вручную читает сотни файлов.

---

## ZONE_9 — Enforcement / Backup / Archive Compression

Цель: ввести строгий mutation guard, validated backup, archive compression и безопасный cleanup.

Режимы enforcement:

```text
MEASURE_ONLY
WARN
WARP_ONLY
BLOCK_LAND
BLOCK_CYCLE
```

Видимая польза: Империум умеет чиститься, архивироваться и не принимать опасные мутации.

---

## 2. Главное правило внедрения

```text
Каждая зона сначала обсуждается.
Затем формализуется.
Затем создаётся WARP-патч с документами, схемами, валидаторами и receipts.
Затем проходит проверка.
Затем Owner review.
Затем land или abort.
```

Исключение: текущий owner foundation lock допускается прямо в Reality как документированная воля Owner-а.
