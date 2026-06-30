# MECHANICUS — устав органа

**schema_version:** `imperium.mechanicus.v0_1`
**charter_version:** `1.0.0`
**parent_charter:** `imperium.astronomicon.v0_1` (ASTRONOMICON.md)
**sibling_charters:** `imperium.administratum.v0_1` (ADMINISTRATUM.md)
**ratified_by:** THRONE
**author_signed:** NOTION_OPUS (CHAT, Opus 4.8)
**storage:** `DOCTRINARIUM/CHARTERS/MECHANICUS.md` (+ `.en.md`)

---

## §0. Природа органа (глобальный принцип всех 9 органов)

МЕХАНИКУС — это **скрипт-первый ИИ-бот (script-first AI bot)**, способный **влиять на поток задачи**.

- **«ИИ» — это автономный бот** с правилами, AST-парсингом, статикой и регрессионными эталонами. **«ИИ» — это НЕ LLM.**
- **Внутри пайплайна — ноль LLM-вызовов.** LLM существуют только как **подписанты** паков (NOTION_OPUS / CODEX / GROK) снаружи. Внутри хуков органа — только детерминированные скрипты.
- Орган влияет на поток через **канонические вердикты** (см. §5): HINT, BLOCK, OVERRIDDEN.
- Все решения **воспроизводимы**: одинаковые входы → одинаковые выходы.

Этот принцип распространяется на все 9 органов Империума и зафиксирован в §0 каждого устава.

## §1. Миссия

МЕХАНИКУС — это **инженер и хранитель механизмов Империума**. Орган выполняет пять переплетённых функций:

1. **Жизненный цикл канон-скриптов** — lint, unit-test, регрессии всех `admin_*.py` / `astra_*.py` / `inq_*.py` / `imperium_*.py`.
2. **Окружение** — stdlib-only enforcement, Python-пины (Windows 3.12 / sandbox 3.13), контроль drift зависимостей.
3. **Обслуживание HARNESS** — ротация `_ADMINISTRATUM/MEMORY/*.jsonl`, вакуум осиротевших receipts, GC старых warp-worktrees.
4. **Миграции схем** — реестр и применение зарегистрированных миграций `SCHEMA_KNOWN.json`, форматов receipt, версий уставов.
5. **Мета-проверки E3-runner'ов** — `test_*_e3.py` должны быть Windows-safe (utf8 reconfigure + ASCII labels + `python` команда, не `python3`).

Каждый орган Империума — тяжёлая боевая единица. Чем больше МЕХАНИКУС МОЖЕТ делать детерминированно, тем выше инженерное качество всего Империума.

## §2. Хуки в Cycle (точки вмешательства)

МЕХАНИКУС встраивается в `astra_cycle.py` через семь канонических хуков. Все хуки изолированы через `subprocess` и работают под **FAIL_CLOSED**: падение хука блокирует цикл.

| # | Хук | Стадия цикла | Скрипты | Может BLOCK? |
|---|---|---|---|---|
| H1 | `POST_ADMIT_HOOK` | сразу после `INBOUND ADMIT` | `mech_depscan.py` | нет (HINT only) |
| H2 | `PRE_PERMIT_HOOK` | перед `PERMIT GRANTED` (THRONE) | `mech_lint.py`, `mech_depscan.py`, `mech_envpin.py` | **да** (MECH_BLOCK_*) |
| H3 | `WARP_TEST_EXTEND` | внутри `WARP_TEST` стадии | `mech_test.py`, `mech_regress.py` | **да** |
| H4 | `PRE_APPLY_HOOK` | после PERMIT, перед COMMIT | `mech_meta_e3.py` | **да** |
| H5 | `POST_LAND_HOOK` | после `LAND` + `PUSH` | `mech_vacuum.py`, `mech_compact.py` (dry-run по умолчанию) | нет |
| H6 | `SCHEDULED_TICK` | ежедневный тик вне cycle | `mech_vacuum.py`, `mech_compact.py` | нет |
| H7 | `ON_DEMAND` | ручной вызов владельца | `mech_build.py`, `mech_migrate.py` | — (manual) |

## §3. Обязанности

МЕХАНИКУС обязан, и только МЕХАНИКУС вправе:

1. **mech_lint** — AST-проверка канон-скриптов: запрещённые импорты, неиспользуемые имена, нарушения стиля.
2. **mech_test** — запуск unit-тестов всех `ORGANS/*/TESTS/test_*.py`.
3. **mech_regress** — фиксированный набор фикстур (`REGRESS/FIXTURES/`), сравнение output с эталонами (`REGRESS/GOLDENS/`).
4. **mech_depscan** — токен-скан исходников на `socket`, `urllib`, `requests`, `http.*` (enforcement инварианта I3 NO_LLM_IN_PIPELINE из Администратума).
5. **mech_envpin** — проверка Python-версии (MAJOR.MINOR совпадение с `ENV/PYTHON_PIN.json`) и состава доступных модулей (`ENV/DEPS_ALLOWED.json`).
6. **mech_compact** — ротация `_ADMINISTRATUM/MEMORY/CURRENT.jsonl` в `YYYY-MM.jsonl` первого числа месяца.
7. **mech_vacuum** — GC warp-worktrees старше `vacuum_age_days` (по умолчанию 30) и orphaned receipts без соответствующих записей в `TASK_REGISTRY`.
8. **mech_migrate** — применение зарегистрированных миграций из `_MECHANICUS/MIGRATIONS/<schema>/<from>_<to>.py` (только ON_DEMAND).
9. **mech_meta_e3** — проверка `test_*_e3.py` на Windows-safe признаки: `sys.stdout.reconfigure(encoding="utf-8")`, ASCII-only printable labels, `python` (не `python3`) в `verify.cmd`.
10. **mech_build** — сборка zip-паков по канон-структуре (как `imp_pack`, но органный, с авто-генерацией `TASK_MANIFEST.json` шаблона).

## §4. Жёсткие запреты

МЕХАНИКУС **никогда** не делает следующее.

1. **no_sign** — не подписывает паки. Подписание — прерогатива подписантов (NOTION_OPUS / CODEX / GROK / OWNER_MANUAL) через `imperium_provenance.py`.
2. **no_permit** — не выдаёт Throne-permit. Это монополия Трона.
3. **no_form_gate** — не валидирует форму пака (схема, обязательные поля). Это монополия Астрономикона (`astra_gate.py`).
4. **no_memory_writes** — не пишет в `_ADMINISTRATUM/MEMORY/`, `TASK_REGISTRY`, `AGENT_REGISTRY`. Это монополия Администратума.
5. **no_silent_block** — любой `MECH_BLOCK_*` обязан содержать `reason` И `recommendation`. Молчаливый блок = нарушение устава.
6. **no_master_mutate** — все операции внутри warp-worktree. Прямой коммит в `master` без прохождения цикла = криминал.
7. **no_network** — `socket`, `urllib`, `requests`, `http.*` запрещены в `mech_*.py` (проверяется самим mech_depscan и инвариантом I2).
8. **no_llm_writes** — результаты LLM-вызова не пишутся в реестры, отчёты, GOLDENS.
9. **no_destructive_default** — `mech_vacuum` и `mech_compact` по умолчанию работают в `--dry-run`. Деструктивный режим требует явного `--confirm`.

## §5. Канонические вердикты

12 канонических вердиктов. Любой другой вердикт — нарушение устава.

### §5.1. Положительные

- **MECH_OK** — все проверки хука прошли успешно.

### §5.2. Информационные (HINT)

- **MECH_HINT_DEPSCAN** — раннее предупреждение на H1 POST_ADMIT о подозрительных импортах. HINT в баннере цикла; не блокирует.
- **MECH_HINT_LINT** — неблокирующие стилевые предупреждения. HINT; не блокирует.

### §5.3. Блокирующие

- **MECH_BLOCK_LINT** — AST/style виоляция (неиспользуемое имя, дублированный импорт, нарушение naming, etc.). Возникает на H2 PRE_PERMIT.
- **MECH_BLOCK_DEPSCAN** — найден запрещённый импорт (`socket`, `urllib`, `requests`, `http`). Заблаговременно ловит нарушение I3 NO_LLM_IN_PIPELINE Администратума.
- **MECH_BLOCK_NETWORK** — эквивалент DEPSCAN с акцентом на сетевые модули. Срабатывает при `import socket` или сетевом вызове в любом виде.
- **MECH_BLOCK_ENVPIN** — Python MAJOR.MINOR не совпадает с `ENV/PYTHON_PIN.json`. Защищает от регрессий типа `python3 vs python` (исторический баг ASTRON-CHARTER v1).
- **MECH_BLOCK_TEST** — `mech_test` вернул rc≠0 хотя бы по одному unit-тесту.
- **MECH_BLOCK_REGRESS** — расхождение output актуального скрипта с эталоном из `REGRESS/GOLDENS/`. Любой diff — блок (regress_diff_threshold = 0).
- **MECH_BLOCK_TIMEOUT** — отдельный тест/проверка превысил `test_timeout_sec` (по умолчанию 60).
- **MECH_BLOCK_META** — `test_*_e3.py` не Windows-safe: отсутствует `sys.stdout.reconfigure(...)`, либо содержит кириллицу в test labels, либо `python3` в `verify.cmd`. Это инвариант, спасший LAND ASTRON-CHARTER v2.

### §5.4. Служебные

- **MECH_OVERRIDDEN** — оператор применил `-ForceMech` для прохода через `MECH_BLOCK_*`. Цикл продолжается; обязательная запись в `_MECHANICUS/ANOMALIES.jsonl`.
- **MECH_FAILED_CLOSED** — сам Механикус упал (rc≠0 или timeout хука). Цикл блокируется. Восстановление только через вмешательство владельца.

## §6. Receipt-схема и mech_report.json

### §6.1. Поля `mech_report.json` (результат каждого хука)

Каждый прогон хука создаёт файл `_MECHANICUS/REPORTS/YYYY-MM-DD/mech_<task>_<hook>_<utc>.json` с полями:

- `utc` — ISO-8601 время прогона.
- `task_id` — идентификатор пака.
- `hook_point` — один из H1..H7.
- `command` — какой `mech_*.py` был вызван и с какими аргументами.
- `scripts_scanned[]` — пути к payload-файлам, прошедшим обработку.
- `lint_findings[]` — список объектов `{file, line, severity, code, message}`.
- `depscan_imports[]` — найденные запрещённые импорты с координатами.
- `test_results[]` — `{test_name, rc, duration_sec, stdout_tail, stderr_tail}`.
- `regress_diff` — `{golden_path, actual_path, unified_diff}` или `null`.
- `env_info` — `{python_version, platform, cwd, executable}`.
- `verdict` — одно из 12 значений (§5).
- `reason` — короткое объяснение вердикта.
- `recommendation` — что должен сделать владелец/подписант, чтобы устранить причину.
- `evidence_path` — путь к полному логу/diff в `_MECHANICUS/REPORTS/`.
- `exit_code` — rc хука.
- `duration_sec` — длительность работы хука.

Отсутствие обязательного поля = валидационная ошибка = `MECH_FAILED_CLOSED`.

### §6.2. Расширение receipt Астры

`_S3_RECEIPTS/<task>.work.json` дополняется блоком `mech` с полями: `verdicts[]`, `hints[]`, `findings_count`, `reports[]` (список путей к `mech_report.json`).

### §6.3. Отдельные BLOCK-receipts

Каждый `MECH_BLOCK_*` дополнительно эмитит `_MECHANICUS/BLOCKS/<task_id>.<utc>.json` с полным `mech_report` + ссылкой на стадию цикла + рекомендацией.

## §7. Архитектура файлов в HARNESS

МЕХАНИКУС хранит всё своё состояние в зоне HARNESS, не в master. В master живёт только устав и (после `MECH-TOOLS-0001`) канонические скрипты.

```
_MECHANICUS\
├── REGISTRIES\
│   └── CANON_SCRIPTS.json        # реестр всех канон-скриптов с версиями и payload-signatures
├── REGRESS\
│   ├── FIXTURES\<script>\        # входы для регрессии
│   ├── GOLDENS\<script>\         # эталоны (immutable без миграции)
│   └── REPORTS\YYYY-MM-DD\       # отчёты прогонов mech_regress
├── ENV\
│   ├── PYTHON_PIN.json           # {windows: 3.12, sandbox: 3.13}
│   └── DEPS_ALLOWED.json         # whitelist stdlib-модулей
├── MIGRATIONS\
│   └── <schema>\<from>_<to>.py   # зарегистрированные миграции
├── REPORTS\
│   └── YYYY-MM-DD\mech_*.json    # вывод каждого хук-прогона
├── BLOCKS\
│   └── <task_id>.<utc>.json      # отдельные BLOCK-receipts (по аналогии с Администратумом)
├── WORKBENCH\
│   └── <task_id>\                # временная рабочая зона build/test, чистится mech_vacuum
└── ANOMALIES.jsonl               # все -ForceMech override записи
```

Принципы: append-only для всех `.jsonl`; rotation по месяцам через новый файл; атомарность через `os.replace`; GOLDENS immutable без явной миграции.

## §8. Канон-скрипты `ORGANS/MECHANICUS/TOOLS/`

Задекларированы здесь; поставляются паком `MECH-TOOLS-0001`:

`mech_init.py`, `mech_lint.py`, `mech_test.py`, `mech_regress.py`, `mech_depscan.py`, `mech_envpin.py`, `mech_compact.py`, `mech_vacuum.py`, `mech_migrate.py`, `mech_meta_e3.py`, `mech_build.py`.

**CLI-стиль (гибрид):**
- Каждый скрипт самостоятелен: `python mech_lint.py <pack_dir> [--strict]` (позиционный pack_dir + флаги, как `imperium_provenance.py`).
- Опциональный входник `mechanicus.py <subcmd> ...` эквивалентен прямому вызову: `mechanicus.py lint <pack_dir>` ≡ `mech_lint.py <pack_dir>`.

Все скрипты — **stdlib only**. Никаких внешних зависимостей. Никаких импортов `socket`, `urllib`, `requests`, `http.*`. Проверяется тестом T4 и инвариантом I2.

## §9. Пороги по умолчанию (переопределяемые)

| Параметр | Значение | Вердикт при нарушении |
|---|---|---|
| `lint_severity_threshold` | error (zero tolerance) | `MECH_BLOCK_LINT` |
| `test_timeout_sec` | 60 | `MECH_BLOCK_TIMEOUT` |
| `regress_diff_threshold` | 0 (любой diff = блок) | `MECH_BLOCK_REGRESS` |
| `envpin_strict_match` | MAJOR.MINOR | `MECH_BLOCK_ENVPIN` |
| `vacuum_age_days` | 30 | (не блок; чистит) |
| `compact_period` | monthly (1-е число) | (не блок; ротация) |
| `depscan_forbidden_count` | 0 | `MECH_BLOCK_DEPSCAN` / `MECH_BLOCK_NETWORK` |

Переопределение: флаг `-ForceMech` в `imp flow/apply` пропускает BLOCK, но **обязательно** пишет в `_MECHANICUS/ANOMALIES.jsonl`.

## §10. Инварианты

- **I1 DETERMINISTIC** — одинаковый вход даёт одинаковый verdict.
- **I2 NO_NETWORK** — никакой `mech_*.py` не импортирует `socket`, `urllib`, `requests`, `http.*`.
- **I3 STDLIB_ONLY** — только стандартная библиотека Python. Никаких pip-зависимостей.
- **I4 FAIL_CLOSED** — падение любого `mech_*.py` останавливает цикл с `MECH_FAILED_CLOSED`.
- **I5 SIGNED_ONLY** — Механикус работает только по пакам, прошедшим `imperium_provenance.verify`.
- **I6 CANONICAL_ORGANS_ONLY** — `target_organ` только из 9 канонических.
- **I7 OVERRIDE_LOGGED** — любой `-ForceMech` обязательно создаёт запись в `ANOMALIES.jsonl`.
- **I8 GOLDEN_IMMUTABLE** — `REGRESS/GOLDENS/` неизменяемы без зарегистрированной миграции в `MIGRATIONS/`.
- **I9 NO_MASTER_MUTATE** — все операции Механикуса — только в warp-worktree. Прямой коммит в master запрещён.

## §11. Версионирование устава

- SemVer `MAJOR.MINOR.PATCH`. MAJOR — изменения вердиктов/инвариантов; MINOR — новые хуки/скрипты; PATCH — текстовые правки.
- Каждая версия — отдельный пак, подписанный Throne-permit.
- Хранение: `DOCTRINARIUM/CHARTERS/MECHANICUS.md` + `.en.md`, рядом с `ASTRONOMICON.md` и `ADMINISTRATUM.md`.
- Двуязычие: RU и EN обязательны и должны быть синхронны.

## §12. CHANGELOG

- **v1.0.0** (2026-06-20, NOTION_OPUS / CHAT / Opus 4.8) — Первая ратифицированная версия. 7 хуков, 12 вердиктов, 9 инвариантов, 10 канон-скриптов задекларированы (поставка через отдельный пак `MECH-TOOLS-0001`).

## §13. Контрольные тесты

Runner: `ORGANS/MECHANICUS/TESTS/test_mech_charter_e3.py`. Запускается как WARP_TEST на каждом цикле, затрагивающем устав или скрипты Механикуса.

- **T1 ENFORCED** — структура устава: RU + EN, все 15 параграфов §0..§14, все 12 вердиктов, все 9 инвариантов, принцип NO_LLM_IN_PIPELINE.
- **T2 ENFORCED-SKIP** — `mech_*.py` CLI smoke (активируется в `MECH-TOOLS-0001`).
- **T3 ENFORCED-SKIP** — `mech_lint` smoke (fixture с запрещённым импортом).
- **T4 ENFORCED-SKIP** — `mech_depscan` smoke (fixture с `import socket`).
- **T5 ENFORCED-SKIP** — `mech_meta_e3` smoke (fixture без `utf8 reconfigure`).
- **T6 PLANNED v0_2** — `mech_test` по всем `ORGANS/*/TESTS/`.
- **T7 PLANNED v0_2** — `mech_regress` с GOLDEN эталонами.
- **T8 PLANNED v0_2** — `mech_envpin` (Python mismatch detection).
- **T9 PLANNED v0_3** — `mech_vacuum` dry-run на fake warp-worktrees.
- **T10 PLANNED v0_3** — полный e2e: пак с broken скриптом → PRE_PERMIT → `MECH_BLOCK_*`.

Падение любого PLANNED-теста при активации форсирует ратификацию новой версии устава с описанием расхождения в §12 CHANGELOG.

## §14. Связь с другими органами

- **Астрономикон** (`ASTRONOMICON.md`) — родительский устав. Его цикл вызывает хуки Механикуса (§2). Любой конфликт решается в пользу Астрономикона.
- **Администратум** (`ADMINISTRATUM.md`) — брат-орган. Механикус работает над физическими механизмами (скрипты, окружение, файлы), Администратум — над фактами (память, реестры, статистика). Механикус **не пишет** в `_ADMINISTRATUM/`, но **читает** через `admin_query.py`/`admin_audit.py` для статистики прогонов.
- **Трон** — верховный валидатор. Любое изменение устава Механикуса требует Throne-permit. Любой `MECH_BLOCK_*` может быть оспорен только через Throne-override (`-ForceMech`), логируемый как аномалия.
- **Доктринариум** — физический хранитель устава. Файл `DOCTRINARIUM/CHARTERS/MECHANICUS.md` — единственный канонический источник.
- **Остальные 5 органов** (Custodes, Inquisition, Officio Agentis, Schola Imperialis, Strategium) — потребители проверок Механикуса. Каждый их канон-скрипт (когда они будут построены) проходит `mech_lint`, `mech_depscan`, `mech_envpin`, `mech_meta_e3`.

---

*Конец устава Механикуса v1.0.0.*
