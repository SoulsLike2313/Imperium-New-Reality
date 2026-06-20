# Устав ASTRONOMICON

- schema_version: `imperium.astronomicon.v0_1`
- charter_version: `1.0.0`
- language: ru (en — см. `ASTRONOMICON.en.md`)
- signed_by: NOTION_OPUS (CHAT / Opus 4.8); Throne-пермит на момент land

---

## §1. Миссия

ASTRONOMICON — **хранитель задачи**. Единственный регистратор и валидатор всех паков перед канонизацией в master.
Ни один пак не приземляется без прохождения цикла Astra.

## §2. Режимы работы

### §2.1. HAND_PACK
- Источник: OWNER_MANUAL или NOTION_OPUS, форма заполняется вручную (`PATCH_PACK_FORM`).
- Astra **сама подписывает** (provenance), регистрирует и исполняет цикл.
- Отчёт — самостоятельный (receipt + memory).

### §2.2. AUTO_PACK
- Источник: Servitor (CODEX / GROK), форма `TASK_PACK_FORM`.
- Astra **регистрирует** пак-задачу. **Без записи в реестре Servitor не работает.**
- Участвуют все 9 органов (детализация — после описания всех уставов и матрицы Throne).

## §3. Цикл валидации

### §3.1. Допуск (3 ворота)
1. `INBOUND` — `astra_gate.validate(pack)`: schema, payload, evidence_level, change_kind.
2. `PROVENANCE` — `imperium_provenance.verify(pack)`: подпись валидна; автор ∈ `{NOTION_OPUS, CODEX, GROK, OWNER_MANUAL}`.
3. `PERMIT` — Throne-пермит = `GRANTED`.

### §3.2. Исполнение
4. `WARP_START` — создание ветки `warp/<task_id>` и worktree вне master.
5. `INTEGRATE` — применение `integration.map` (file → target path).
6. `WARP_TEST` — `verify.cmd` с `rc=0`.
7. `COMMIT` — коммит в warp-ветке с `author=подписант`.

### §3.3. Приземление
8. `PRE_LAND` — снятие untracked-коллизий (warp-ветка авторитетна).
9. `LAND` — `git merge --squash warp/<task_id>` в master, коммит.
10. `PUSH` — `origin master` (если remote сконфигурирован).
11. `CLEANUP` — удаление worktree + ветки.

### §3.4. Фиксация
12. `RECEIPT` — `receipt.json` + `receipt.txt` в `_S3_RECEIPTS\<task_id>.work.{json,txt}`.
13. `MEMORY` — append-only запись в `ADMINISTRATUM_MEMORY.jsonl`.

### §3.5. Паспорт задачи (формат лога)
Обязательные поля паспорта:
- Пришёл от (author / form / model)
- Контур (WINDOWS_PC / SANDBOX / …)
- Пермит (THRONE = GRANTED)
- Валидация (ASTRONOMICON gate INBOUND + WARP_TEST → verdict)
- Память (ADMINISTRATUM индекс рецептов)
- Land (`base_sha → land_sha`)
- Итог (verdict)

## §4. Запреты (жёсткие)

1. **Не push** без green `WARP_TEST`.
2. **Не сохранять секреты/ключи** в receipt и память.
3. **Не выдавать `CYCLE_OK`** при любом красном этапе.
4. **Не трогать master напрямую** — только через `warp/<task_id>` + squash.
5. **Не bypass'ить** `gate` / `provenance` / `permit` ни при каких обстоятельствах.
6. **Не подписывать чужие паки и не модифицировать payload** (роль валидатора).
   - **Исключение:** в `HAND_PACK` Astra может подписать пак сама (см. §2.1).

## §5. Канонические вердикты

Каждый красный вердикт сопровождается **причиной** (`reason`) и **рекомендацией** (`recommendation`).

| Verdict | Когда возникает |
|---|---|
| `CYCLE_OK` | Полный цикл прошёл, master сдвинут |
| `CYCLE_DRYRUN_OK` | Драй-ран зелёный, ожидание `apply` |
| `CYCLE_REJECTED_GATE` | `INBOUND` провалил (schema/payload/evidence) |
| `CYCLE_REJECTED_PROVENANCE` | Подпись битая, нет автора или identity-mismatch |
| `CYCLE_REJECTED_PERMIT` | Throne ≠ GRANTED |
| `CYCLE_FAIL_INTEGRATE` | `integration.map` не применился |
| `CYCLE_FAIL_WARP_TEST` | `verify.cmd` rc ≠ 0 |
| `CYCLE_FAIL_LAND` | merge/squash не прошёл даже после `PRE_LAND` |
| `CYCLE_FAIL_PUSH` | remote не принял (auth/conflict/network) |
| `TASK_NOT_REGISTERED` | Servitor пришёл с `task_id`, которого нет в реестре |
| `TASK_PENDING` | Зарегистрирован, но ещё не провалидирован |
| `TASK_BLOCKED_SERVITOR` | Явный стоп Servitor (Astra не пропустила) |

## §6. Формат receipt.json (минимум)

```json
{
  "schema_version": "imperium.astronomicon.receipt.v0_1",
  "task_id": "ASTRON-...",
  "pack_digest": "sha256:...",
  "verdict": "CYCLE_OK",
  "reason": null,
  "recommendation": null,
  "mode": "HAND_PACK",
  "started_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "finished_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "author": "NOTION_OPUS",
  "form": "CHAT",
  "model": "Opus 4.8",
  "contour": "WINDOWS_PC",
  "stages": [
    {"name":"INBOUND","rc":0,"ts":"...","msg":"ADMIT digest=..."}
  ],
  "git": {
    "base_sha": "...",
    "branch": "warp/<task_id>",
    "land_sha": "...",
    "push_remote": "origin master"
  },
  "declared_evidence_level": "E3",
  "execution_log_path": "...",
  "memory_index_entry": "<offset/uri>"
}
```

Принцип: **человек и машина** одинаково должны понять, что произошло и почему.

## §7. Архитектура «Ядро × Обвязка» (Windows-style)

- **Ядро (REALITY / master):** только канон — устав, инструменты, receipts выполненных задач.
- **Обвязка (HARNESS):** реестр задач, формы, наряды (work-order), рабочее состояние, временные файлы, прогонки.

Правило: **состояние никогда не лежит в ядре**. Только канонизированный результат.

### §7.1. Размещение в HARNESS
- `E:\IMPERIUM_HARNESS\_ASTRA\TASK_REGISTRY.jsonl` — append-only индекс задач.
- `E:\IMPERIUM_HARNESS\_ASTRA\TASKS\<task_id>\` — детали задачи + черновик пака + work-order.
- `E:\IMPERIUM_HARNESS\_S3_RECEIPTS\<task_id>.work.{json,txt}` — рабочие receipts (далее канонизируются в master).
- `E:\IMPERIUM_HARNESS\_S3_RECEIPTS\ADMINISTRATUM_MEMORY.jsonl` — append-only память.

## §8. Блокировка Servitor (AUTO_PACK)

Sevitor запускается строго с аргументом `--task-id <id>`:
1. Servitor приходит к Astra с `task_id`.
2. Astra смотрит `TASK_REGISTRY.jsonl`.
3. Решение:
   - не найден → `TASK_NOT_REGISTERED` → **STOP** (причина: «Astra не пропустила: задача не зарегистрирована»).
   - найден, но не валидирован → `TASK_PENDING` → **STOP** (причина: «Astra не пропустила: задача ждёт валидации»).
   - найден и валидирован → выдаётся **work-order** (JSON с подписью Astra) → Servitor продолжает.

## §9. Формы паков

- **`PATCH_PACK_FORM`** — для `HAND_PACK`. См. `ASTRONOMICON_FORMS/PATCH_PACK_FORM.md` + `.template.json`.
- **`TASK_PACK_FORM`** — для `AUTO_PACK`. См. `ASTRONOMICON_FORMS/TASK_PACK_FORM.md` + `.template.json`.

Заполненная форма → полировка NOTION_OPUS → готовый пак, проходящий gate.

## §10. Инварианты (всегда истинны)

1. К master без warp не касаться: всегда squash из `warp/<task_id>`.
2. Каждый пак подписан. `HAND_PACK`: подпись Astra (как от автора через делегацию). `AUTO_PACK`: подпись Servitor.
3. Секреты/ключи **никогда** не попадают в receipt и память.
4. Ядро × Обвязка: в master — только канон и receipts; всё состояние — в HARNESS.
5. Нет задачи в реестре → Servitor не работает (Astra блокирует).
6. `ADMINISTRATUM_MEMORY` = append-only, не переписывается.

## §11. Версионирование устава

- `charter_version` (semver): `1.0.0` → `1.1.0` (доп. правила, без слома совместимости) → `2.0.0` (несовместимые изменения).
- `schema_version`: `imperium.astronomicon.v0_1` → `v0_2` (структурные изменения схем receipt/registry/work-order).
- `CHANGELOG` — внутри устава (§12).
- Каждая новая версия устава — **обычный пак** (`ASTRON-CHARTER-000N`), проходящий цикл Astra (мета-валидация).
- На каждую версию — Throne-пермит. После описания всех 9 органов вводится **матрица Throne** (верховная валидация).

## §12. CHANGELOG

- **v1.0.0** (первая редакция): режимы `HAND_PACK` / `AUTO_PACK`, форматы receipt, формы паков (PATCH/TASK), инварианты, тесты `cycle` + `collision` как `ENFORCED`, `check-task` / `HAND_E2E` / `form→pack` как `PLANNED`.

## §13. Контрольные тесты

| # | Тест | Статус v1.0.0 | План |
|---|---|---|---|
| 1 | E3 cycle 4/4 (land / discard / tamper / unsigned) | **ENFORCED** | — |
| 2 | E3 PRE_LAND collision (untracked снимается, land проходит) | **ENFORCED** | — |
| 3 | E3 check-task → `TASK_NOT_REGISTERED` | PLANNED | v0_2 |
| 4 | E3 HAND_PACK end-to-end (Astra сама подписывает + исполняет) | PLANNED | v0_3 |
| 5 | E3 форма → пак (форма даёт валидный пак, проходящий gate) | PLANNED | v0_3 |

Прогонка `ENFORCED`-тестов = условие принятия любого пака от ASTRONOMICON.
Периодические прогонки → красный тест → переписывание соответствующей части устава или инструментов Astra.
Результаты прогонок — версионно в `E:\IMPERIUM_HARNESS\_ASTRA\TEST_RUNS\<utc>.json`.

## §14. Доктринариум

Устав хранится в:
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON.md` (RU, рабочий).
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON.en.md` (EN, перевод).

DOCTRINARIUM отвечает за хранение, версионирование и периодические прогонки. Astra исполняет; Doctrinarium хранит и проверяет на чистоту и работоспособность.
