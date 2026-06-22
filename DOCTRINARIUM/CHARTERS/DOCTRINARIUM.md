# УСТАВ ОРГАНА DOCTRINARIUM

- **task_id:** DOCTR-CHARTER-0001
- **version:** 1.0.0
- **lineage:** master d8027a81598f007a46cc85dcdf3cbc73b76b05b3 (after INQ-TOOLS-0001 land)
- **target_organ:** DOCTRINARIUM (этот документ хранится в DOCTRINARIUM)
- **canonical_organ:** DOCTRINARIUM
- **echelon:** 1 (Астрономикон → Администратум → Механикус → Инквизиция → **Доктринариум**)
- **schema_version:** imperium.charter.v0_1

---

## §0. NO_LLM_IN_PIPELINE (глобальный принцип всех 9 органов)

Доктринариум — это **script-first AI**. LLM-выводы внутри `doctrinarium_*.py`, `imperium_first_boot_*.py`, `kernel_write_guard_*.py` и любых других tools этого органа **ЗАПРЕЩЕНЫ**. AI ≠ LLM. Решения о admission/canon/PASS/WARN/BLOCK/E-уровне принимаются **только детерминированной логикой**:

- проверка наличия файлов на диске;
- sha256-сравнение содержимого;
- regex против KERNEL_PATTERNS;
- валидация JSON-схем (JSON-Schema-2020-12 либо jsonschema-pure-python без сети);
- табличное сравнение evidence_level → разрешённая authority;
- подсчёт receipt-цепочки.

Любая попытка вызвать LLM из tools Доктринариума — инцидент `DOCTR_FAILED_CLOSED`. Документируется в `_HARNESS/_NEGATIVE_EXPERIENCE/`.

LLM-выводы происходят **только снаружи** — на стороне подписантов pack-а (NOTION_OPUS / CODEX / GROK). Внутри Доктринариума — ноль LLM, ноль сети, ноль недетерминизма.

---

## §1. Миссия

Доктринариум — **хранилище исполнительных законов и канона Империума**. Это не runtime-проверка кода (Механикус) и не семантическая проверка содержимого (Инквизиция). Это **верхний слой**: что вообще имеет право стать каноном Империума, по каким исполнительным законам Империум работает, и какие заявления (claims) запрещены без соответствующих доказательств.

### §1.1. Семь зон ответственности

1. **Execution law** — авторские law-документы под `LAWS/`. Существующий слой: clean-and-honest, evidence-vault batch (dry-run/plan/execution/receipt), trinity-related (patch, hygiene, plus-bilingual), repo-hygiene-lane, storage-index, intelligence-pack, ghost-evolve-v2, owner-gated-hygiene, h-contour-patch-backup. Новый слой из `DOCTR-TOOLS-0001`: kernel-boundary, canonical-pipeline, entry-protocol-for-llm, emperor-seal-placeholder, role-registry.
2. **Canon admission** — матрицы `MATRICES/CANON_ADMISSION_MATRIX.{json,md}`. Определяют: что → `CANON_ACTIVE`, что → `CANDIDATE_V0_1`, что → `BLOCK`.
3. **Forbidden claims** — реестр того, что орган, актёр или таск-пак не имеет права заявлять. Примеры: runtime authority без E3+ replay, throne permit без активного gateway, kernel-write без Emperor Seal, fake-green без receipts.
4. **Evidence levels (E0–E6)** — Доктринариум является owner-of-record таблиц соответствия `evidence_level → разрешённая authority`. E0 = только claim. E1 = файл существует. E2 = self-test декларация. E3 = воспроизводимый replay через `_HARNESS/RUNNER/e3_runner.py`. E4–E6 — multi-actor counter-signs + temporal locks (резерв на будущие эшелоны).
5. **Role registry doctrine** — реестр ролей актёров Империума и их допустимых mandates. На v1.0.0: OWNER_MANUAL (sovereign), THRONE (gateway), LOGOS_PRIME (стратегический планировщик, currently NOTION_OPUS), SPECULUM (DORMANT — резерв форка), SERVITOR_PRIME (исполнитель, currently CODEX + GROK), ROGUE_TRADER + FREE_ARCHITECT (PLANNED для эшелонов 4+).
6. **Kernel boundary** — спецификация `KERNEL_PATTERNS`: glob-паттерны файлов, неприкосновенных без Emperor Seal. Точный список — в `LAWS/KERNEL_BOUNDARY_CONTRACT_V0_1.md` (приходит в `DOCTR-TOOLS-0001`).
7. **Canonical pipeline** — формальный 7-stage contract жизненного цикла pack-а: PACK_AUTHORED → SHAKEDOWN_LOCAL → PR_OR_BUNDLE → INQUISITION_RED_TEAM → MECHANICUS_TOOL_VALIDATE → THRONE_PERMIT_OR_OBSERVER → LAND_TO_MASTER. Подробности — в `LAWS/CANONICAL_PIPELINE_V0_1.md` (приходит в `DOCTR-TOOLS-0001`).

---

## §2. Что Доктринариум НЕ делает

Чтобы не размывать границы органов:

- **НЕ владеет runtime tools** для Mechanicus / Inquisition / Custodes. У каждого свои toolchain-ы.
- **НЕ выпускает Throne-permit**. Throne — это gateway ВЫШЕ 9 органов (см. `ORGANS/_CORE_GOVERNANCE/THRONE/THRONE_GATEWAY_CONTRACT_V0_1.md` и `REQUIRED_9_ORGANS_V0_1.json:throne_scope`).
- **НЕ принимает решений по конкретным task-pack-ам**. Это компетенция: Inquisition (red-team), Mechanicus (tool/receipt validation), Astronomicon (admission), Officio_Agentis (final response discipline).
- **НЕ изменяет Constitution / Passport / GOVERNANCE_INDEX**. Любая поправка к kernel-документам требует Emperor Seal (`DOCTR-EMPEROR-SEAL-0001`, отдельный pack эшелона 1).
- **НЕ имеет write-доступа за пределы `clone\` (active root)**. AGENTS.md root contract: "Read/write/mutate only inside this root". Никакой Ancient / VM2 / VM3 / quarantine.
- **НЕ оценивает trust-score актёров**. Trust-score — компетенция Inquisition (см. `ORGANS/INQUISITION/TRUST/authors.json`).

---

## §3. Что является каноном (admission boundaries)

Документ становится `CANON_ACTIVE` при выполнении **ВСЕХ** условий:

1. Лежит в `clone\` (active root), а не в Ancient / VM2 / VM3 / quarantine / SUPPORT.
2. Прошёл self-test уровня E3+ через `_HARNESS/RUNNER/e3_runner.py --organ <name>`.
3. Имеет receipt в `_HARNESS/_RUNS/<utc>/RESULTS.json` со статусом PASS (schema `inq.e3_results.v0_1`).
4. Подписан валидным актёром из ROLE_REGISTRY с непустым trust-score (Inquisition not BANNED).
5. Не содержит секретов / PI-markers / fake-green-markers (`inq_secrets`, `inq_pi_scan`, `inq_audit` всё PASS).
6. Записан в `GOVERNANCE_INDEX.json:documents[].status = "CANON_ACTIVE"` ИЛИ упомянут в `ORGAN_CARD.json` соответствующего органа в полях `validators` / `owned_matrices` / `owned_metrics`.

Документ остаётся `CANDIDATE_V0_1` если выполнены только условия 1–4, но не 5–6. **Candidate не имеет authority** до утверждения. Любая ссылка на candidate как на canon — fake-green инцидент.

---

## §4. Файловая структура DOCTRINARIUM

После `DOCTR-CHARTER-0001` + `DOCTR-TOOLS-0001` lands структура органа выглядит так:

```
ORGANS/DOCTRINARIUM/
├── ORGAN_CARD.json                              # canonical, edit-merge через DOCTR-TOOLS-0001
├── ORGAN_CONTRACT.md                            # canonical, edit-merge
├── READ_FIRST_GHOST_EVOLVE_PACKET.md            # canonical
├── LAWS/
│   ├── (22 existing law documents)
│   ├── KERNEL_BOUNDARY_CONTRACT_V0_1.md         # из DOCTR-TOOLS-0001
│   ├── CANONICAL_PIPELINE_V0_1.md               # из DOCTR-TOOLS-0001
│   ├── ENTRY_PROTOCOL_FOR_LLM_V0_1.md           # из DOCTR-TOOLS-0001
│   ├── EMPEROR_SEAL_PLACEHOLDER_V0_1.md         # из DOCTR-TOOLS-0001
│   └── ROLE_REGISTRY_V0_1.json                  # из DOCTR-TOOLS-0001
├── MATRICES/
│   ├── (4 existing matrices с .json + .md дублёрами)
│   └── KPD_METRIC_SPEC_V0_1.{md,json}           # из DOCTR-TOOLS-0001 (доктринальная спека)
├── SCHEMAS/                                     # NEW directory (из DOCTR-TOOLS-0001)
│   └── role_registry.schema.json
├── TOOLS/                                       # NEW directory (из DOCTR-TOOLS-0001)
│   └── doctrinarium_integrity_validator_v0_1.py
├── TESTS/                                       # NEW directory
│   ├── test_doctr_charter_e3.py                 # из этого pack-а (DOCTR-CHARTER-0001)
│   └── test_doctr_tools_e3.py                   # из DOCTR-TOOLS-0001
├── BLOCK/                                       # canonical, без изменений
└── TASK_PARTICIPATION/                          # edit-merge ORGAN_TOOL_AND_RECEIPT_INVENTORY.json
```

Также в `DOCTR-TOOLS-0001` уезжают в core-зону:

```
ORGANS/_CORE_GOVERNANCE/
├── SCHEMAS/
│   ├── entry_protocol_ack.schema.json           # NEW
│   └── kernel_integrity_snapshot.schema.json    # NEW
└── TOOLS/
    ├── imperium_first_boot_v0_1.py              # NEW
    └── kernel_write_guard_v0_1.py               # NEW (OBSERVER mode v0_1)
```

---

## §5. Связь с GOVERNANCE_INDEX (authority order)

Доктринариум **подчиняется** существующей цепочке authority из `GOVERNANCE_INDEX.json:authority_order`:

1. **Emperor Passport** (rank 1) — выше Доктринариума. Поправки — только через Emperor Seal.
2. **Constitution of the Imperium** (rank 2) — выше Доктринариума. Поправки — только через Emperor Seal.
3. **AGENTS.md** (rank 3) — boot-law entrypoint каждого исполнителя. Доктринариум читает её первой.
4. **Organ contracts and read-first files** (rank 4) — сюда попадают LAWS/ Доктринариума.
5. **Astronomicon taskpacks** (rank 5) — current task execution.
6. **Tool cards and validators** (rank 6) — Mechanicus territory.
7. **Reports and receipts** (rank 7) — Inquisition + Administratum territory.

Доктринариум **не конкурирует** с этой цепочкой — он её формализует через `LAWS/ROLE_REGISTRY_V0_1.json`, `LAWS/KERNEL_BOUNDARY_CONTRACT_V0_1.md`, `LAWS/CANONICAL_PIPELINE_V0_1.md`.

---

## §6. Связь с другими 8 органами Империума

**Отдаёт:**

- → **Officio_Agentis**: ROLE_REGISTRY (для role-routing и owner-facing language authority).
- → **Strategium**: KPD_METRIC_SPEC (доктринальная спецификация метрики; Strategium реализует tools).
- → **Inquisition**: KERNEL_PATTERNS (для detection unauthorized kernel-write).
- → **Astronomicon**: CANONICAL_PIPELINE (для admission и route manifests).
- → **Mechanicus**: ENTRY_PROTOCOL_FOR_LLM (для tool-invocation discipline).
- → **Custodes**: ORGAN_LIFE_ZONE granular rules (через core CONTRACT references).
- → **Schola_Imperialis**: reusable-lesson templates (через `LAWS/CLEAN_AND_HONEST_SYSTEM_LAW_V0_1.md` already).
- → **Administratum**: evidence-vault doctrines (большая часть существующих LAWS уже про это).

**Получает:**

- ← **Inquisition**: красные вердикты, если pack нарушает doctrine. Doctrinarium reads `inq_*` reports как input для admission decision.
- ← **Mechanicus**: receipts с evidence_level. Doctrinarium табулирует level → authority.
- ← **Astronomicon**: taskpack identity + route manifest. Doctrinarium проверяет admission.
- ← **Administratum**: continuity packs + closure receipts.

---

## §7. KERNEL_PATTERNS (kernel boundary, краткая редакция)

Полная спецификация — в `LAWS/KERNEL_BOUNDARY_CONTRACT_V0_1.md` (приходит в DOCTR-TOOLS-0001). Краткий список того, что нельзя писать без Emperor Seal:

- `ORGANS/_CORE_GOVERNANCE/CONSTITUTION/*` (вся папка)
- `ORGANS/_CORE_GOVERNANCE/EMPEROR/*`
- `ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json`
- `ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json`
- `ORGANS/_CORE_GOVERNANCE/CORE_*_CONTRACT_V*.md`
- `ORGANS/_CORE_GOVERNANCE/ORGAN_LIFE_ZONE_CONTRACT_V*.md`
- `ORGANS/_CORE_GOVERNANCE/QUARANTINE_USE_BAN_CONTRACT_V*.md`
- `ORGANS/_CORE_GOVERNANCE/SUPPORT_ZONE_CONTRACT_V*.md`
- `AGENTS.md` (root)
- `DOCTRINARIUM/CHARTERS/*` (этот файл и его братья)

`kernel_write_guard_v0_1.py` (OBSERVER mode на v0_1) детектит попытки записи в эти пути и логирует в `_HARNESS/LEDGERS/`. BLOCKING mode активируется только после `DOCTR-EMPEROR-SEAL-0001`.

---

## §8. Canonical pipeline (7 stages, краткая редакция)

Полная спецификация — в `LAWS/CANONICAL_PIPELINE_V0_1.md` (приходит в DOCTR-TOOLS-0001). Краткое описание стадий:

1. **PACK_AUTHORED** — LOGOS_PRIME (NOTION_OPUS) собирает pack из payload файлов + build script + signature.
2. **SHAKEDOWN_LOCAL** — `python3 _HARNESS/RUNNER/e3_runner.py --organ <NAME>` проходит локально, RESULTS.json со статусом PASS.
3. **PR_OR_BUNDLE** — pack доставляется OWNER_MANUAL либо PR-ом, либо ops-bundle .zip-ом.
4. **INQUISITION_RED_TEAM** — `inq_pi_scan`, `inq_secrets`, `inq_audit` на payload-файлах. Все три PASS.
5. **MECHANICUS_TOOL_VALIDATE** — каждый новый tool имеет tool-card, schema-валидацию, command-policy entry.
6. **THRONE_PERMIT_OR_OBSERVER** — на эшелоне 1 (без Emperor Seal) Throne работает в OBSERVER mode, выдаёт `throne_permit_receipt.v0_1` со status=OBSERVER.
7. **LAND_TO_MASTER** — squash-merge в master с commit-message по golden template (task / branch / base / landed / Authored-by / identity_sig).

Каждая стадия = одна receipt в `_HARNESS/_RUNS/<utc>/`.

---

## §9. Forbidden claims (детально)

Запрещённые заявления, которые любой актёр обязан проверять перед утверждением:

- **"Runtime authority подтверждена"** без E3+ self-test receipt. На E1 (file exists) authority НЕ runtime, она только структурная.
- **"Throne permit выдан"** без активного gateway. На эшелоне 1 — OBSERVER, не PERMIT.
- **"Канон обновлён"** без записи в `GOVERNANCE_INDEX.json:documents[]`.
- **"All tests passing"** без RESULTS.json со status=PASS и непустым `tests[]` массивом.
- **"Kernel-документ обновлён"** без Emperor Seal receipt.
- **"Trust-score актёра подтверждён"** без записи в `ORGANS/INQUISITION/TRUST/authors.json`.
- **"Multi-actor counter-sign"** без минимум 2 ECDSA/Ed25519 подписей в provenance.

Любое из этих заявлений без соответствующего receipt — **fake-green** инцидент. Доктринариум — author of fake-green-detection doctrine, Inquisition — runtime enforcer.

---

## §10. Provenance & E3 test plan

Этот charter покрывается `ORGANS/DOCTRINARIUM/TESTS/test_doctr_charter_e3.py`. Покрытие (минимум 12 тестов):

| T#  | Тест                                                                 |
|-----|----------------------------------------------------------------------|
| T01 | `DOCTRINARIUM/CHARTERS/DOCTRINARIUM.md` существует                   |
| T02 | `DOCTRINARIUM/CHARTERS/DOCTRINARIUM.en.md` существует                |
| T03 | RU содержит все секции §0–§11                                        |
| T04 | EN содержит все секции §0–§11 (parallel structure)                   |
| T05 | RU header содержит `DOCTR-CHARTER-0001`                              |
| T06 | RU header содержит `version: 1.0.0`                                  |
| T07 | RU header содержит `imperium.charter.v0_1`                           |
| T08 | RU header содержит real master sha (`d8027a8`)                       |
| T09 | RU §0 и EN §0 содержат "NO_LLM_IN_PIPELINE"                          |
| T10 | EN файл содержит английские маркеры ("Mission", "Authority")         |
| T11 | RU файл содержит ≥ 30% кириллицы                                     |
| T12 | Размер RU и EN в разумных границах                                   |

Запуск: `python3 _HARNESS/RUNNER/e3_runner.py --organ DOCTRINARIUM --select test_doctr_charter_e3.py`.

Provenance:

- **task_id:** DOCTR-CHARTER-0001
- **branch:** warp/DOCTR-CHARTER-0001
- **base:** d8027a81598f007a46cc85dcdf3cbc73b76b05b3
- **authored_by:** NOTION_OPUS (CHAT / Opus 4.5)
- **lineage:** after INQ-TOOLS-0001 land
- **evidence_level on land:** E3 (e3_runner replay)
- **throne_status:** OBSERVER (Emperor Seal не активирован на эшелоне 1)

---

## §11. Future amendments

- **Поправки к этому уставу** — через `DOCTR-CHARTER-0002+` packs. Каждая поправка bump version (1.0.0 → 1.1.0 для дополнений, 1.0.0 → 2.0.0 для breaking).
- **Поправки к Constitution / Passport** — НЕ через charter, а через `DOCTR-EMPEROR-SEAL-0001` (pack 0002 этого эшелона) и далее `EMPEROR_SEAL_ACTIVATION` task.
- **Добавление 10-го органа** — bumps `REQUIRED_9_ORGANS_V0_1.json` → `REQUIRED_10_ORGANS_V0_2.json` и требует Emperor Seal.
- **Активация SPECULUM** (currently DORMANT) — через owner-decision в `GOVERNANCE_INDEX.json:owner_decisions_required_for_final_canon[]` пункт "Confirm whether SPECULUM becomes a baseline organ or remains a candidate organ".

---

*Конец устава DOCTRINARIUM v1.0.0.*
