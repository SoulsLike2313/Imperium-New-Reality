# ADMINISTRATUM — устав органа

**schema_version:** `imperium.administratum.v0_1`
**charter_version:** `1.0.0`
**parent_charter:** `imperium.astronomicon.v0_1` (ASTRONOMICON.md)
**ratified_by:** THRONE
**author_signed:** NOTION_OPUS (CHAT, Opus 4.8)
**storage:** `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md` (+ `.en.md`)

---

## §0. Природа органа (глобальный принцип всех 9 органов)

ADMINISTRATUM — это **script-first AI bot**, способный **влиять на поток задачи**.

- **«AI» означает автономный бот** с правилами, эвристиками, статистикой, словарями. **«AI» НЕ означает LLM.**
- **Pipeline — без единого LLM-вызова.** LLM существуют только как **подписанты** паков (NOTION_OPUS / CODEX / GROK), которые СОЗДАЮТ паки извне. Внутри хуков органа — только детерминированные скрипты.
- Орган воздействует на поток через **канонические вердикты** (см. §5), которые меняют ход цикла Астры: HINT, BLOCK, RECORD.
- Все решения органа **воспроизводимы**: те же входы → те же выходы.

Этот принцип распространяется на все 9 органов Империума и фиксируется в §0 каждого устава.

## §1. Миссия

ADMINISTRATUM — **память империи и её бухгалтер**. Орган выполняет четыре связанные функции одновременно:

1. **Память** — единственный append-only журнал всего, что когда-либо происходило в потоке задач.
2. **Бухгалтерия** — хранитель receipts, audit trail, ANOMALIES.
3. **Реестр** — единственный источник правды о задачах, агентах, органах, правах, ротациях ключей.
4. **Архивариус-аналитик** — детерминированная ретроспектива: похожие задачи, паттерны ошибок, статистика, аномалии.

Каждый орган Империума — большая боевая единица. Чем больше Администратум УМЕЕТ детерминированно делать, тем доказуемее и чище работа всего Империума.

## §2. Хуки в Cycle (точки вмешательства)

ADMINISTRATUM встраивается в цикл Астры (`astra_cycle.py`) на четырёх каноничных точках. Каждый хук изолирован через `subprocess` и работает по принципу **FAIL_CLOSED**: падение хука блокирует цикл.

| # | Хук | Стадия Cycle | Скрипты | Может BLOCK? |
|---|---|---|---|---|
| H1 | `POST_ADMIT_HOOK` | сразу после `INBOUND ADMIT` | `admin_recall.py`, `admin_anomaly.py` | нет (только HINT в баннер) |
| H2 | `PRE_PERMIT_HOOK` | до `PERMIT GRANTED` (THRONE) | `admin_quota.py`, `admin_drift.py` | **да** (ADMIN_BLOCK_*) |
| H3 | `PRE_APPLY_HOOK` | после `PERMIT`, до `WARP_START` | финальный `admin_anomaly.py` | **да** |
| H4 | `MEMORIZE_HOOK` | финал цикла (всегда, любой вердикт) | `admin_memorize.py` | — (только запись) |

Изоляция: Cycle вызывает `python ORGANS/ADMINISTRATUM/TOOLS/admin_*.py` через subprocess. Никакого in-process import — чтобы падение Администратума не унесло Cycle.

FAIL_CLOSED: если любой `admin_*.py` упал (rc≠0 или таймаут), Cycle обязан вернуть `ADMIN_FAILED_CLOSED` и не двигаться дальше. Память критична — без неё работа Империума запрещена.

## §3. Обязанности

ADMINISTRATUM обязан, и только Администратум вправе:

1. **MEM_APPEND** — поддерживать append-only лог всех CYCLE_* в `MEMORY/CURRENT.jsonl` с ротацией по месяцам.
2. **RECEIPTS** — гарантировать запись `_S3_RECEIPTS/<task_id>.work.{json,txt}` для каждого цикла (атомные рецепты, не append).
3. **TASK_REGISTRY** — вести `REGISTRIES/TASK_REGISTRY.jsonl` как зеркало Астры с расширенной историей статусов (все промежуточные вердикты, не только финальные).
4. **AGENT_REGISTRY** — `REGISTRIES/AGENT_REGISTRY.jsonl`: подписанты (NOTION_OPUS, CODEX, GROK), ключи (идентификаторы, не сами секреты), история ротаций.
5. **ORGANS_LEDGER** — `REGISTRIES/ORGANS_LEDGER.jsonl`: какой орган когда вмешивался в какой цикл и с каким вердиктом.
6. **AUDIT_TRAIL** — индекс «кто-что-когда» по последним N циклам; быстрый ответ на запросы вида «что делал NOTION_OPUS вчера».
7. **REDACTION** — стирать любые совпадения `REDACTION_PATTERNS.json` (api_key, token, secret, password, hex длиной ≥32, и т.п.) из всего, что пишется в журналы. Подсчёт стираний попадает в receipt.
8. **MEMORY_RECALL** — детерминированный поиск «было ли уже похожее» по интенту: нормализация → токенизация → Jaccard/keyword similarity. **Без embeddings, без LLM.**
9. **STATS** — `STATS/YYYY-MM-DD.json`: суточные сводки ADMIT/REJECT/CYCLE_OK/CYCLE_FAIL_* + baseline-объёмы для z-score.

Дополнительно (производное от §3.1–§3.9):

- **SCHEMA_DRIFT_DETECTOR** — поддерживать `SCHEMA_KNOWN.json` со всеми известными `schema_version` (паков, провенанса, receipt, charter). Любой неизвестный → ADMIN_BLOCK_DRIFT, требующий явной ратификации.
- **AUTO_TAG** — словарь `TAGS_DICT.json` (regex → tag) для авто-классификации задач при записи в memory.

## §4. Запреты

ADMINISTRATUM **никогда не**:

1. **NO_MUTATE** — редактирует, переписывает или удаляет прошлые записи в `MEMORY/*.jsonl`, `REGISTRIES/*.jsonl`, `ANOMALIES.jsonl`. Только append.
2. **NO_SECRETS** — пишет секреты/ключи/токены в clear text в любой файл под `_ADMINISTRATUM/` или `_S3_RECEIPTS/`.
3. **NO_SIGN** — подписывает паки. Подписи — исключительное право подписантов (NOTION_OPUS/CODEX/GROK/OWNER_MANUAL); Администратум только верифицирует, что подпись была проверена Астрой.
4. **NO_PERMIT** — выдаёт Throne-permit. Это исключительное право Throne.
5. **NO_FORM_GATE** — валидирует форму пака. Это исключительное право Астры (`astra_gate.py`).
6. **NO_SILENT_BLOCK** — блокирует поток молча. Любой ADMIN_BLOCK_* обязан содержать `reason` и `recommendation` в receipt.
7. **NO_LLM_WRITES** — пишет в `MEMORY/*.jsonl` результат любого LLM-вывода без детерминированной проверки. Поле в memory заполняется только после прохождения скриптовой валидации.

## §5. Канонические вердикты

ADMINISTRATUM выдаёт **11 канонических вердиктов**. Любой другой вердикт — нарушение устава.

### §5.1. Информационные (не блокируют поток)

- **ADMIN_RECORDED** — успешная запись в `MEMORY/CURRENT.jsonl`. Финальный вердикт любого цикла на стадии H4.
- **ADMIN_HINT_RECALL** — `admin_recall.py` нашёл одну или несколько похожих прошлых задач. Печатает HINT в баннер цикла; не блокирует.
- **ADMIN_HINT_PATTERN** — `admin_recall.py` нашёл прошлый CYCLE_FAIL_* с похожей причиной и его решение. Печатает HINT; не блокирует.

### §5.2. Блокирующие (останавливают цикл)

- **ADMIN_BLOCK_RATE** — превышен `rate_limit.per_author_hour` (по умолчанию 30/час).
- **ADMIN_BLOCK_LOOP** — `task_id` повторился больше 5 раз за 24 часа (петля).
- **ADMIN_BLOCK_DUP** — один и тот же `payload_signature` подряд 3 и более раз (fake-retry).
- **ADMIN_BLOCK_COOLDOWN** — 3 подряд CYCLE_FAIL_* от того же автора; cooldown 10 минут.
- **ADMIN_BLOCK_BURST** — z-score объёма за окно > 3 от суточного baseline.
- **ADMIN_BLOCK_DRIFT** — `schema_version` отсутствует в `SCHEMA_KNOWN.json`. Требует явной ратификации.

### §5.3. Служебные

- **ADMIN_OVERRIDDEN** — администратор использовал флаг `-ForceAdmin` для прохода через ADMIN_BLOCK_*. Цикл продолжается, в `ANOMALIES.jsonl` обязательная запись.
- **ADMIN_FAILED_CLOSED** — сам Администратум упал (rc≠0 или таймаут). Цикл блокируется. Восстановление — через ручное вмешательство владельца.

## §6. Receipt-схема и запись memory.jsonl

### §6.1. Поля записи в `MEMORY/CURRENT.jsonl` (обязательные)

Каждая запись — одна строка JSON с минимум следующими полями:

```json
{
  "utc": "2026-06-20T10:21:13Z",
  "task_id": "ADMIN-CHARTER-0001",
  "title": "...",
  "author": "NOTION_OPUS",
  "form": "CHAT",
  "model": "Opus 4.8",
  "target_organ": "DOCTRINARIUM",
  "verdict": "CYCLE_OK",
  "reason": "",
  "git": { "base_sha": "...", "new_sha": "..." },
  "payload_signature": "sha256:...",
  "stages": ["INBOUND:ADMIT", "PROVENANCE:OK", "PERMIT:GRANTED", "WARP_START:OK", "INTEGRATE:OK", "WARP_TEST:OK", "COMMIT:OK", "LAND:OK", "PUSH:OK"],
  "organs_seen": [{ "organ": "ADMINISTRATUM", "verdict": "ADMIN_RECORDED" }],
  "tags": ["charter", "doctrinarium", "organ-setup"],
  "receipt_path": "_S3_RECEIPTS/ADMIN-CHARTER-0001.work.json",
  "admin_verdict": "ADMIN_RECORDED"
}
```

Любое поле может присутствовать в расширенном виде; **отсутствие обязательного поля = ошибка валидации = ADMIN_FAILED_CLOSED**.

### §6.2. Дополнения к основному receipt от Астры

Когда Cycle пишет `_S3_RECEIPTS/<task>.work.json`, в него добавляется блок `admin`:

```json
{
  "admin": {
    "verdicts": ["ADMIN_HINT_RECALL", "ADMIN_RECORDED"],
    "hints": [{ "kind": "RECALL", "text": "..." }],
    "recall_top": [{ "task_id": "...", "similarity": 0.42, "verdict": "CYCLE_OK" }],
    "quota_state": { "per_author_hour": 7, "limit": 30 },
    "drift_diff": null,
    "overrides": [],
    "redactions_count": 0
  }
}
```

### §6.3. Отдельные рецепты на BLOCK

Каждый `ADMIN_BLOCK_*` дополнительно порождает файл `_ADMINISTRATUM/BLOCKS/<task_id>.<utc>.json` с полями `reason`, `evidence`, `recommendation`, и снимок счётчиков на момент решения (для воспроизводимости).

## §7. Архитектура файлов в HARNESS

Administratum хранит всё своё состояние в **HARNESS-зоне**, а не в master-каноне. В master хранится только устав и канон-скрипты (после `ADMIN-TOOLS-0001`).

```
E:\IMPERIUM_HARNESS\
├── _ADMINISTRATUM\
│   ├── MEMORY\
│   │   ├── CURRENT.jsonl              ← текущий месяц (append)
│   │   ├── 2026-06.jsonl              ← ротация по месяцам
│   │   └── 2026-05.jsonl
│   ├── REGISTRIES\
│   │   ├── TASK_REGISTRY.jsonl
│   │   ├── AGENT_REGISTRY.jsonl
│   │   └── ORGANS_LEDGER.jsonl
│   ├── STATS\
│   │   └── 2026-06-20.json
│   ├── BLOCKS\
│   │   └── <task_id>.<utc>.json       ← по одному файлу на каждый BLOCK
│   ├── ANOMALIES.jsonl                ← журнал override + аномалий
│   ├── SCHEMA_KNOWN.json              ← известные версии схем (drift-detect)
│   ├── TAGS_DICT.json                 ← regex → tag
│   └── REDACTION_PATTERNS.json        ← regex секретов
└── _S3_RECEIPTS\
    ├── ASTRON-CHARTER-0001.work.{json,txt}
    ├── ADMIN-CHARTER-0001.work.{json,txt}
    └── ADMINISTRATUM_MEMORY.jsonl     ← унаследованный общий лог (зеркалируется в MEMORY/CURRENT.jsonl)
```

Принципы:

- **append-only** для всех `.jsonl` файлов. Любая запись — `open(path, "a", encoding="utf-8")`. Никаких `"w"`, никаких `os.remove`, никаких truncate.
- **rotation** по месяцам только через создание нового файла, без удаления старых.
- **atomicity** — receipts (`work.json`/`work.txt`) пишутся через `os.replace` (atomic rename).

## §8. Канон-скрипты `ORGANS/ADMINISTRATUM/TOOLS/`

Канон-инструменты Администратума — отдельный пак `ADMIN-TOOLS-0001`, который придёт после ратификации устава. В уставе они декларируются:

| Скрипт | CLI | Назначение |
|---|---|---|
| `admin_init.py` | `--harness-root PATH` | Bootstrap пустых файлов на новой машине |
| `admin_memorize.py` | `--receipt PATH` | Append записи о цикле в `MEMORY/CURRENT.jsonl` |
| `admin_recall.py` | `--intent STR --top K` | Jaccard/keyword-поиск похожих прошлых задач |
| `admin_quota.py` | `--author A` | RATE_LIMIT проверка |
| `admin_anomaly.py` | `--window N` | sliding-window + z-score detector |
| `admin_drift.py` | `--pack PATH` | SCHEMA_DRIFT детектор |
| `admin_redact.py` | `--in PATH --out PATH` | Стирание секретов из текста |
| `admin_stats.py` | `--date YYYY-MM-DD` | Агрегация суточных/недельных сводок |
| `admin_query.py` | `--task ID \| --author A \| --date D` | CLI поиска |
| `admin_audit.py` | `--last N` | Индекс AUDIT_TRAIL |
| `admin_tag.py` | `--text STR` | Авто-теги по TAGS_DICT (regex → tag) |

Все скрипты — **stdlib only**. Никаких внешних зависимостей. Никаких импортов `socket`, `urllib`, `requests`, `http.client`, `http.server`. Это проверяется тестом T5 (см. §13).

## §9. Пороги по умолчанию

Пороги хранятся в `_ADMINISTRATUM/SCHEMA_KNOWN.json` под ключом `admin_defaults` и могут быть перехвачены без изменения устава.

| Параметр | Значение | Вердикт при превышении |
|---|---|---|
| `per_author_hour` | 30 паков | `ADMIN_BLOCK_RATE` |
| `task_repeat_24h` | 5 повторов | `ADMIN_BLOCK_LOOP` |
| `digest_repeat_inrow` | 3 | `ADMIN_BLOCK_DUP` |
| `fail_cooldown` | 3 FAIL → 10 мин | `ADMIN_BLOCK_COOLDOWN` |
| `burst_zscore` | > 3.0 | `ADMIN_BLOCK_BURST` |
| `schema_drift` | любой неизвестный schema_version | `ADMIN_BLOCK_DRIFT` |

Override: флаг `-ForceAdmin` в `imp flow/apply` пропускает BLOCK, но **обязательно** порождает запись в `ANOMALIES.jsonl` с указанием инициатора и причины.

## §10. Инварианты

8 инвариантов, проверяемых тестами (см. §13):

- **I1 APPEND_ONLY** — любой файл в `_ADMINISTRATUM/` только растёт. Truncate/overwrite запрещены.
- **I2 NO_SECRETS** — ни одного совпадения `REDACTION_PATTERNS` в записях `MEMORY/*.jsonl`.
- **I3 NO_LLM_IN_PIPELINE** — ни один `admin_*.py` не импортирует `socket`, `urllib`, `requests`, `http.*`. Никаких сетевых вызовов из хуков.
- **I4 DETERMINISTIC** — одинаковые входы (memory snapshot + входной пакет) → одинаковые выходы и вердикты.
- **I5 FAIL_CLOSED** — падение любого `admin_*.py` (rc≠0, таймаут) останавливает цикл с `ADMIN_FAILED_CLOSED`.
- **I6 SIGNED_ONLY** — в `MEMORY/CURRENT.jsonl` пишутся только записи о паках с проверенным `imperium_provenance.verify`.
- **I7 CANONICAL_ORGANS_ONLY** — в `organs_seen[]` допустимы только 9 канонических органов: ADMINISTRATUM, ASTRONOMICON, CUSTODES, DOCTRINARIUM, INQUISITION, MECHANICUS, OFFICIO_AGENTIS, SCHOLA_IMPERIALIS, STRATEGIUM.
- **I8 OVERRIDE_LOGGED** — любой `-ForceAdmin` обязательно порождает запись в `ANOMALIES.jsonl`.

## §11. Версионирование устава

- **SemVer** `MAJOR.MINOR.PATCH`.
  - `MAJOR` — изменения списка вердиктов §5 или инвариантов §10.
  - `MINOR` — новые скрипты §8 или новые хуки §2.
  - `PATCH` — текстовые правки, не меняющие поведение.
- Каждая версия — отдельный пак, **подписанный Throne-permit**.
- Хранение: `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md` (RU) + `ADMINISTRATUM.en.md` (EN), рядом с `ASTRONOMICON.md`.
- Билингва: RU и EN обязательны и должны быть согласованы.

## §12. CHANGELOG

- **v1.0.0** (2026-06-20, NOTION_OPUS / CHAT / Opus 4.8) — Первая ратифицированная версия. 4 хука, 11 вердиктов, 8 инвариантов, 10 канон-скриптов задекларированы (поставка отдельным паком ADMIN-TOOLS-0001).

## §13. Контрольные тесты

Контрольный runner: `ORGANS/ADMINISTRATUM/TESTS/test_admin_charter_e3.py`. Запускается WARP_TEST на каждом цикле, затрагивающем устав или скрипты органа.

### §13.1. ENFORCED (v1.0.0)

- **T1** — структура устава: RU+EN, все 15 параграфов §0..§14 на месте, все 11 вердиктов §5 упомянуты, все 8 инвариантов §10 упомянуты.
- **T2** — `admin_*.py` пока не в каноне (придут в ADMIN-TOOLS-0001). В уставе T2 декларирован как ENFORCED со SKIP до ADMIN-TOOLS-0001 land. После ratification ADMIN-TOOLS-0001 — переходит в ENFORCED PASS.
- **T3** — append-only smoke: создать временный `.jsonl`, попытаться открыть в режиме `"w"` через тестовую обёртку → fail/refuse.
- **T4** — redaction smoke: подать `"api_key=ABC123"` в эталонный текст → на выходе `[REDACTED]`.
- **T5** — NO_NETWORK: проверить, что `admin_*.py` не содержат токенов `import socket`, `import urllib`, `import requests`, `import http`. Активируется после ADMIN-TOOLS-0001.

### §13.2. PLANNED

- **T6 v0_2** — RECALL по фикстуре: засеять 5 записей в тестовую `MEMORY/CURRENT.jsonl`, поиск выдаёт ожидаемый top-K.
- **T7 v0_2** — DRIFT: пакет с неизвестным `schema_version` → `ADMIN_BLOCK_DRIFT`.
- **T8 v0_2** — QUOTA: 31 пакет/час → `ADMIN_BLOCK_RATE` на 31-м.
- **T9 v0_3** — OVERRIDE: `-ForceAdmin` пропускает пакет, `ANOMALIES.jsonl` получает запись.
- **T10 v0_3** — e2e: полный цикл со всеми хуками (recall + quota + drift + memorize).

### §13.3. Триггер переписывания устава

Провал любого PLANNED-теста при его активации (переходе в ENFORCED) обязывает к ratification новой версии устава с описанием расхождения в §12 CHANGELOG.

## §14. Связь с Астрономиконом и Throne

- **Астрономикон** (`ASTRONOMICON.md`) — родительский устав. Его цикл вызывает хуки Администратума §2. Любое расхождение между уставами разрешается в пользу Астрономикона.
- **Throne** — верховный валидатор. Любое изменение устава Администратума требует Throne-permit. Любой `ADMIN_BLOCK_*` может быть оспорен только через Throne-override (`-ForceAdmin`), который сам логируется как аномалия.
- **Doctrinarium** — физический хранитель устава. Файл `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md` — единственный канонический источник.
- **Остальные 6 органов** (Custodes, Inquisition, Mechanicus, Officio Agentis, Schola Imperialis, Strategium) — потребители памяти Администратума. Они читают через `admin_query.py` и `admin_audit.py`, но не пишут в `_ADMINISTRATUM/` напрямую.

---

*Конец устава Администратума v1.0.0.*
