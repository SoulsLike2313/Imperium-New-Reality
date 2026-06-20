# УСТАВ ОРГАНА INQUISITION (ИНКВИЗИЦИЯ)

- **task_id:** INQ-CHARTER-0001
- **version:** 1.0.0
- **lineage:** master 60b426f6ae48 (after MECH-CHARTER-0001 land)
- **target_organ:** DOCTRINARIUM (этот документ хранится в DOCTRINARIUM)
- **canonical_organ:** INQUISITION
- **echelon:** 1 (Астрономикон → Администратум → Механикус → **Инквизиция**)
- **schema_version:** imperium.charter.v0_1

---

## §0. NO_LLM_IN_PIPELINE (глобальный принцип всех 9 органов)

Инквизиция — это **script-first AI**. LLM-вызовы внутри cycle, hooks, скриптов и пайплайнов органа **ЗАПРЕЩЕНЫ**. AI ≠ LLM. Решения вердикта принимаются **только детерминированной логикой**: regex, энтропия Шеннона, статистика по реестрам, проверки подписей, табличный trust-score. Любая попытка вызвать LLM из inq_*.py — это инцидент INQ_FAILED_CLOSED.

LLM-вызовы происходят **только снаружи** — на стороне подписантов (NOTION_OPUS / CODEX / GROK), создающих паки. Внутри Инквизиции — ноль LLM, ноль сети, ноль недетерминизма.

---

## §1. Миссия

Инквизиция — **семантический страж Империума**. В отличие от Механикуса, который проверяет статический синтаксис кода, Инквизиция проверяет **смысл и содержимое данных и поведение акторов**.

Области ответственности:

1. **Охота на секреты** — поиск API-ключей, токенов, OAuth-credentials, AWS-ключей, PEM-блоков, JWT и подобного в payload-файлах пака.
2. **PI-defense** — детект prompt-injection маркеров в markdown / content / комментариях пака.
3. **Семантические аномалии** — подозрительные паттерны в авторстве, форме, цели, change_kind, target_organ.
4. **Forensic / расследование инцидентов** — трейс по task_id через реестры Администратума и собственные журналы.
5. **Ведение Redact-паттернов** — поддержка REDACTION_PATTERNS.json (потребитель — Администратум).
6. **Trust-score авторов и форм** — динамический рейтинг NOTION_OPUS / CODEX / GROK / OWNER_MANUAL по истории вердиктов.
7. **BAN-list** — блокировка авторов и хэшей payload при рецидиве с обязательным следом в ANOMALIES.

### §1.1. PURGE_PROTOCOL (DORMANT)

Инквизиция получает дополнительный мандат: **по собственной воле уничтожать то, что не является частью Империума**. Эта обязанность по умолчанию **ЗАМОРОЖЕНА** и активируется только при выполнении всех условий §10.

На момент v1.0.0 устава: PURGE_PROTOCOL = DORMANT, разрешена только **инвентаризация** (inq_purge_scan → PURGE_TARGETS/), физическое перемещение в _QUARANTINE/ — запрещено.

---

## §2. Файловая структура _INQUISITION\

Орган владеет каталогом `E:\IMPERIUM_HARNESS\_INQUISITION\` со следующей **канонической** структурой (все 10 узлов):

```
_INQUISITION\
  ANOMALIES.jsonl                      # append-only главный реестр (секреты/PI/паттерны)
  INCIDENTS\
    YYYY-MM-DD\
      <task_id>.json                   # расследования инцидентов
  REPORTS\
    YYYY-MM-DD\
      inq_<task_id>_<utc>.json         # по-паковые рапорты inq_report
  BLOCKS\
    <task_id>.<utc>.json               # история INQ_BLOCK_* вердиктов
  SIGNATURES\
    PI_SIGNATURES.json                 # охотничьи трофеи: PI-маркеры
    SECRETS_PATTERNS.json              # regex для секретов
    REDACTION_PATTERNS.json            # экспортируется в Администратум
  TRUST\
    authors.json                       # trust-score по подписантам
    forms.json                         # trust-score по формам (CHAT/CLI)
  BAN_LIST.jsonl                       # append-only баны c proof=<ANOMALIES ref>
  PURGE_TARGETS\                       # DORMANT — реестр кандидатов на чистку
    <utc>.json
  INQUISITION_LEDGER.jsonl             # общий журнал ВСЕХ вердиктов (OK/HINT/BLOCK)
  ARCHIVE\
    YYYY-Q<n>\                        # квартальный ротируемый архив
  TRACE_CACHE\
    <task_id>.json                     # кэш forensic-сборок
```

Инициализация — командой `inq_init`. Структура создаётся идемпотентно.

---

## §3. Канон-скрипты (10 инструментов)

Все скрипты — stdlib only, без сети, FAIL_CLOSED. Поставка — отдельный пак `INQ-TOOLS-0001` (после уставов первого эшелона). До его LAND тесты T2-T5 в режиме ENFORCED-SKIP.

| # | Скрипт | Назначение |
|---|---|---|
| 1 | `inq_secrets` | regex + Shannon-entropy scan payload на секреты (sk-, AKIA, BEGIN PRIVATE KEY, ghp_, etc.) |
| 2 | `inq_pi_scan` | поиск PI-маркеров в markdown/content («ignore previous», «system:», role-switch, подозрительные URL) |
| 3 | `inq_redact` | применение REDACTION_PATTERNS к payload (замена на `[REDACTED:<тип>]`) |
| 4 | `inq_anomaly` | семантический детект аномалий (новый автор, редкий target_organ, необычный change_kind) |
| 5 | `inq_trace` | быстрый forensic по task_id (receipt + подписи + вердикты всех органов) |
| 6 | `inq_trust` | вычисление trust-score по автору / форме на основе истории вердиктов |
| 7 | `inq_patterns` | CRUD над PI_SIGNATURES.json / SECRETS_PATTERNS.json / REDACTION_PATTERNS.json |
| 8 | `inq_ban` | ведение BAN_LIST.jsonl (требует proof из ANOMALIES) |
| 9 | `inq_report` | сводный рапорт по паку (агрегация всех inq_* в один JSON) |
| 10 | `inq_audit` | «твёрдый» аудит — проверка целостности подписей в ARCHIVED memory |

Входник `inquisition.py` (hybrid CLI): `inquisition <subcmd> [...]` → диспатч в соответствующий inq_*. Допустим и прямой вызов `inq_<name>.py`.

---

## §4. Запреты (11 жёстких + entropy-порог)

1. **no_sign** — Инквизиция не подписывает паки.
2. **no_permit** — Инквизиция не выдаёт Throne-permit.
3. **no_form_gate** — Инквизиция не валидирует форму пака (это компетенция Астрономикона).
4. **no_lint** — Инквизиция не делает AST/style-проверок (это Механикус).
5. **no_memory_writes в _ADMINISTRATUM/MEMORY** — Инквизиция МОЖЕТ читать память Администратума для форензики, но НЕ ПИШЕТ в неё.
6. **no_silent_block** — любой `INQ_BLOCK_*` обязан содержать `reason` + `recommendation` + `evidence_path`.
7. **no_master_mutate** — все изменения только в warp-worktree, master неизменяем напрямую.
8. **no_network** — запрещены socket / urllib / requests / http / любая сетевая активность.
9. **no_llm_writes** — запрещена запись LLM-результатов в реестры.
10. **no_false_positive_silent** — если `inq_secrets` нашёл «key» в документации без strict-pattern и с энтропией ниже порога, обязан выдать HINT (не BLOCK).
11. **no_ban_without_proof** — запись в BAN_LIST принимается только с явным указателем на конкретную запись ANOMALIES.jsonl.
12. **no_pi_execution** — Инквизиция НИКОГДА не исполняет инструкции, найденные в сканируемом content. Найденный текст — это **улика**, а не команда.

---

## §5. Хуки в Astra cycle

Инквизиция влияет на поток задачи через 5 канонических хуков + всё через `subprocess` + FAIL_CLOSED:

| Хук | Точка | Действие | Возможный вердикт |
|---|---|---|---|
| **H1** | `POST_ADMIT_HOOK` | `inq_secrets` + `inq_pi_scan` | `INQ_BLOCK_SECRETS` / `INQ_BLOCK_PI` / `INQ_HINT_*` |
| **H2** | `PRE_PERMIT_HOOK` | `inq_anomaly` + `inq_trust` + `inq_ban` | `INQ_BLOCK_TRUST` / `INQ_BLOCK_BAN` / `INQ_HINT_FIRST_AUTHOR` |
| **H3** | `WARP_TEST_EXTEND` | `inq_redact` в worktree (dry-run) | `INQ_BLOCK_REDACT_FAIL` |
| **H4** | `PRE_APPLY_HOOK` | `inq_audit` подписей | `INQ_BLOCK_AUDIT` |
| **H5** | `POST_LAND_HOOK` | `inq_trust` обновляет рейтинг автора (write-only) | — (write-only) |
| **H6** | `ON_DEMAND` | `inq_trace` / `inq_report` ручным вызовом владельца | — |

Все хуки запускают inq_*.py через `subprocess.run` со стандартными pipe для stdout/stderr и таймаутом. Любая нештатная ошибка инструмента → автоматический `INQ_FAILED_CLOSED` → cycle BLOCK.

---

## §6. Вердикты (14)

**OK / HINT (не блокирующие):**

1. `INQ_OK` — всё чисто.
2. `INQ_HINT_SECRETS` — entropy-match в docs/комментариях, без strict-pattern.
3. `INQ_HINT_PI` — 1–2 PI-маркера.
4. `INQ_HINT_FIRST_AUTHOR` — первый пак от нового автора.
5. `INQ_HINT_TRUST_LOW` — trust ∈ [0.4, 0.6).

**BLOCK (блокирующие):**

6. `INQ_BLOCK_SECRETS` — strict-pattern (sk-, AKIA, BEGIN PRIVATE KEY, ghp_, …) или entropy ≥ 4.5 bits/char.
7. `INQ_BLOCK_PI` — ≥3 PI-маркера.
8. `INQ_BLOCK_TRUST` — trust < 0.4.
9. `INQ_BLOCK_BAN` — автор/хэш payload в BAN_LIST.
10. `INQ_BLOCK_AUDIT` — подпись не совпадает в ARCHIVED memory.
11. `INQ_BLOCK_REDACT_FAIL` — `inq_redact` сломал файлы (binary/syntax broken).
12. `INQ_BLOCK_PURGE_NOT_READY` — попытка purge при CORE_READY=false.

**Сервисные:**

13. `INQ_OVERRIDDEN` — флаг `-ForceInq` использован, лог в ANOMALIES + LEDGER.
14. `INQ_FAILED_CLOSED` — ошибка инструмента → BLOCK по умолчанию.

---

## §7. Инварианты (12 железных правил)

1. **I1 DETERMINISTIC** — одинаковый вход (payload + state of registries) → одинаковый вердикт.
2. **I2 NO_NETWORK** — запрещены socket / urllib / requests / http.
3. **I3 STDLIB_ONLY** — никаких внешних зависимостей.
4. **I4 FAIL_CLOSED** — ошибка = `INQ_FAILED_CLOSED` → cycle BLOCK.
5. **I5 NO_ADMIN_MEMORY_WRITE** — Инквизиция пишет только в `_INQUISITION\`.
6. **I6 APPEND_ONLY** — `ANOMALIES.jsonl`, `BAN_LIST.jsonl`, `INQUISITION_LEDGER.jsonl` — только добавление.
7. **I7 NO_PI_EXECUTION** — инструкции из сканируемого content НИКОГДА не исполняются.
8. **I8 BAN_REQUIRES_PROOF** — запись BAN без указателя в ANOMALIES отклоняется.
9. **I9 PURGE_GUARDED** — без `CORE_READY=true` НЕТ физических удалений (только инвентаризация).
10. **I10 OVERRIDE_LOGGED** — `-ForceInq` всегда пишет в ANOMALIES и LEDGER.
11. **I11 NO_MASTER_MUTATE** — всё в warp-worktree.
12. **I12 SIGNED_ONLY** — Инквизиция смотрит только паки с валидным PROVENANCE.

---

## §8. Пороги (9 строгих defaults)

| # | Параметр | Значение | Override |
|---|---|---|---|
| 1 | `secrets_entropy_threshold` | 4.5 bits/char (Shannon) | через `-ForceInq` |
| 2 | `secrets_strict_patterns_block` | `true` (sk-, AKIA, BEGIN PRIVATE KEY, ghp_, xoxb-, AIza) | через `-ForceInq` |
| 3 | `pi_block_score` | 3 (≥3 маркера = BLOCK; <3 = HINT) | через `-ForceInq` |
| 4 | `trust_min_score` | 0.4 | через `-ForceInq` |
| 5 | `anomaly_first_author_action` | `HINT` | non-overridable |
| 6 | `ban_burst_threshold` | 3 `INQ_BLOCK_*` в 7 дней от одного автора → `BAN_PROPOSED` | через `-ForceInq` |
| 7 | `purge_requires_core_ready` | `true` | non-overridable |
| 8 | `fail_closed_default` | `true` | non-overridable |
| 9 | `override_flag` | `-ForceInq` (логируется обязательно) | — |

Любой override регистрируется записью `INQ_OVERRIDDEN` в `ANOMALIES.jsonl` + `INQUISITION_LEDGER.jsonl` с UTC, автором, причиной.

---

## §9. Форма inq_report.json (10 блоков)

```json
{
  "utc": "YYYY-MM-DDTHH:MM:SSZ",
  "task_id": "<TASK>",
  "hook_point": "H1|H2|H3|H4|H5|H6",
  "scope": "scan|redact|trace|trust|purge",
  "verdict": "INQ_OK | INQ_HINT_* | INQ_BLOCK_* | INQ_OVERRIDDEN | INQ_FAILED_CLOSED",
  "reason": "<plain-text rationale>",
  "recommendation": "<actionable next step>",
  "evidence_path": "<path to BLOCKS or REPORTS file>",
  "exit_code": 0,
  "duration_sec": 0.0,

  "secrets_findings": [
    {"file": "...", "line": 0, "pattern_id": "...", "severity": "...", "entropy_score": 0.0, "redacted_preview": "..."}
  ],
  "pi_findings": [
    {"file": "...", "line": 0, "marker_id": "...", "context_tail": "..."}
  ],
  "anomaly_findings": [
    {"kind": "...", "evidence_key": "...", "evidence_value": "..."}
  ],
  "trust_assessment": {
    "author": "...", "score_before": 0.0, "score_after": 0.0, "sample_size": 0, "last_seen_utc": "..."
  },
  "ban_check": {"hit": false, "ban_id": null, "reason": null},
  "audit_check": {"ok": true, "mismatches": [], "archive_path": "..."},
  "redact_dryrun": {"files_changed": 0, "size_delta_bytes": 0, "broken_files": []},
  "purge_scan_findings": [
    {"path": "...", "reason_not_imperium": "..."}
  ],
  "env_info": {"python_version": "3.x", "platform": "win32|linux", "cwd": "..."}
}
```

Все 10 блоков обязательны (`purge_scan_findings` может быть пустым массивом, если scope ≠ purge).

---

## §10. PURGE_PROTOCOL (DORMANT — резервная функция)

Инквизиция получает мандат «уничтожать то, что не является частью Империума», но активация **заморожена** до выполнения всех 7 условий:

1. **Инвентаризация сейчас** — разрешён только `inq_purge_scan`, который вносит кандидатов в `PURGE_TARGETS/<utc>.json`. Удаление запрещено.
2. **Критерий «not_imperium»** — файл считается кандидатом, если он:
   - находится **вне git-дерева** `E:\IMPERIUM_REALITY` (т.е. не tracked в master), **И**
   - находится **вне** канонических подпапок `E:\IMPERIUM_HARNESS\` (`TOOLS\PY`, `_S3_RECEIPTS`, `_INBOX\PACKS`, `_STAGING`, `_ASTRA`, `_ADMINISTRATUM`, `_MECHANICUS`, `_INQUISITION`, …).
3. **WHITELIST.json** — явный список путей/glob, считающихся Империумом, ведётся **владельцем вручную**. Файл в WHITELIST никогда не попадает в PURGE_TARGETS.
4. **Активация** — снятие DORMANT требует **двух условий одновременно**:
   - флаг `OWNER_MANUAL --activate-purge`;
   - LAND-запись `core_ready=true` в реестре Администратума.
5. **Quarantine, не delete** — даже при `CORE_READY=true` Инквизиция НЕ удаляет файлы напрямую, а перемещает их в `_QUARANTINE/<task_id>/<original_path>/` с обязательством task_id и UTC.
6. **Каждый purge-акт = отдельный PACK** — `change_kind=DELETE`, `target_organ=INQUISITION`, `submitted_by=OWNER_MANUAL`. Проходит через Астрономикон → Администратум → Механикус → Инквизицию обычным cycle.
7. **CORE_READY** определение — это булев флаг, истинный только при выполнении:
   - LANDED уставы всех 9 органов (ADMINISTRATUM, ASTRONOMICON, CUSTODES, DOCTRINARIUM, INQUISITION, MECHANICUS, OFFICIO_AGENTIS, SCHOLA_IMPERIALIS, STRATEGIUM);
   - LANDED устав TRONE_CHARTER;
   - LANDED все TOOLS-паки соответствующих органов.

Попытка purge при невыполнении любого из условий → `INQ_BLOCK_PURGE_NOT_READY`.

---

## §11. CLI (hybrid)

Два эквивалентных способа вызова — на выбор подписанта:

```text
# 1) Через входник
python inquisition.py secrets    --pack <pack_dir>
python inquisition.py pi-scan    --pack <pack_dir>
python inquisition.py redact     --pack <pack_dir> --dryrun
python inquisition.py anomaly    --task <task_id>
python inquisition.py trace      --task <task_id>
python inquisition.py trust      --author <name>
python inquisition.py patterns   --list | --add | --remove
python inquisition.py ban        --add <author|hash> --proof <ANOMALIES_REF>
python inquisition.py report     --pack <pack_dir>
python inquisition.py audit      --quarter YYYY-Q<n>

# 2) Напрямую
python inq_secrets.py --pack <pack_dir>
python inq_pi_scan.py --pack <pack_dir>
# ... и так далее
```

Все скрипты возвращают `exit_code`:
- `0` — `INQ_OK` / `INQ_HINT_*` (HINT не блокирует cycle).
- `1` — любой `INQ_BLOCK_*`.
- `2` — `INQ_FAILED_CLOSED`.
- `3` — `INQ_OVERRIDDEN` (override применён, но событие зафиксировано).

---

## §12. Lifecycle и ротация

- `ANOMALIES.jsonl`, `BAN_LIST.jsonl`, `INQUISITION_LEDGER.jsonl` — append-only.
- Ежеквартально (`Q1`, `Q2`, `Q3`, `Q4`): срез файлов перемещается в `ARCHIVE/YYYY-Q<n>/`, текущий файл начинается заново. Архив **неизменяем**.
- `REPORTS/`, `BLOCKS/`, `INCIDENTS/` — по UTC-дате, без срока хранения (хранятся минимум 1 год).
- `TRACE_CACHE/` — TTL 30 дней, может быть очищен `inq_trace --refresh`.
- `PURGE_TARGETS/` — сохраняется до фактического переноса в _QUARANTINE/ или явного `inq_purge_clear`.

---

## §13. Версионирование устава

- Изменение этого документа = NEW_FILE/REFACTOR pack через Astra с `target_organ=DOCTRINARIUM`.
- Версия повышается семантически (MAJOR.MINOR.PATCH):
  - MAJOR — изменение инвариантов / запретов / вердиктов с потерей обратной совместимости.
  - MINOR — новые скрипты, новые пороги, расширение хуков.
  - PATCH — текстовые правки, уточнения формулировок без изменения семантики.
- Любое изменение порогов §8 — это минимум MINOR + явная запись в ANOMALIES.jsonl от имени OWNER_MANUAL.

---

## §14. Версия

- **v1.0.0** — первичная редакция. Третий и последний устав первого эшелона (Астрономикон ✅, Администратум ✅, Механикус ✅, **Инквизиция ⟵ ЭТОТ**).
- После LAND этого устава первый эшелон считается **сформированным по уставам**; следующая фаза — TOOLS-паки органов и большой PATCH-тест через 4 органа.
