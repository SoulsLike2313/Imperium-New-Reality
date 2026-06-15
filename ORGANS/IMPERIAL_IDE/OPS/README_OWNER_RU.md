# IMPERIAL IDE :: OPERATIONAL ENGINE V0.1 (для владельца)

Это **операционное ядро** Imperial IDE. Оно превращает набор красивых панелей
в рабочую систему, которая закрывает полный цикл задачи **изнутри IDE**, без
ручного перетаскивания ZIP.

Статус: `CANDIDATE_NOT_CANON` (кандидат, не канон). Всё работает в режиме
**dry-run**, kernel не трогается, реальное исполнение выключено. Validated push
разрешён и ожидается только после validation, scope check, secret check и task policy.

## Что закрывает цикл

```
идея владельца
  -> задача (Task Console)
  -> taskpack (Taskpack Builder)
  -> регистрация в Astronomicon
  -> launch card
  -> servitor handoff (dry-run)
  -> validation
  -> receipts
  -> administratum bundle gate
  -> inquisition anti-fake-green
  -> owner summary
  -> git closure (commit/push или объяснение почему нельзя)
  -> next task recommendation
```

15 этапов реализованы в `ENGINE/imperium_ops/lifecycle.py` и видны и в CLI, и в TUI.

## Быстрый старт (PC)

```powershell
# из корня репозитория
$env:IMPERIUM_ROOT = "E:\IMPERIUM_NEW_GENERATION_NEW_REALITY"

# 1) Прогнать smoke (доказательство, что всё живо)
python ORGANS\IMPERIAL_IDE\OPS\TESTS\ops_smoke.py

# 2) Открыть операционную консоль (TUI)
python ORGANS\IMPERIAL_IDE\OPS\TUI\imperial_ide_ops_tui.py

# 3) Прогнать одну задачу целиком через CLI (dry-run)
python ORGANS\IMPERIAL_IDE\OPS\CLI\imperial_ide_ops_cli.py lifecycle ^
    --title "Mechanicus tool registry editor" ^
    --goal "Add a Mechanicus tool registry editor"
```

## CLI команды

| Команда | Что делает |
|---|---|
| `classify` | определить тип/scope/risk задачи и task_id |
| `build-taskpack` | собрать taskpack + zip + sha256 + precheck |
| `register` | зарегистрировать taskpack в Astronomicon (dry-run STAGING) |
| `launch-card` | показать launch card |
| `lifecycle` | прогнать все 15 этапов и показать вердикт |
| `safety` | показать safety-статус (все опасные флаги OFF) |
| `git-status` | состояние git репозитория |
| `validate-receipt <path>` | проверить receipt + fake-green risk |

## Безопасность (по умолчанию всё закрыто)

- `AllowReal: false`
- `Unsafe shell: blocked`
- `Live LLM backend: off`
- `Real servitor execution: blocked`
- `Validated push`: только после validation, scope check, secret check и task policy
- **Нет PASS без receipt.** Inquisition anti-fake-green ловит "зелёнку" без доказательств.

## Честные ограничения V0.1

1. Servitor/Codex/LLM — это **заглушки**: интерфейс готов, реального вызова моделей нет.
2. GUI-панели описаны в ROADMAP; в этом пакете рабочая оболочка — **TUI + CLI**.
3. `.ps1` лаунчеры для Windows PC; в Linux-песочнице запускается напрямую `python`.
4. Регистрация и git-closure по умолчанию **dry-run** (пишут в `ORGANS/IMPERIAL_IDE/OPS/STAGING/`, не в kernel).

См. `ROADMAP/IMPERIAL_IDE_OPERATIONAL_ROADMAP_RU.md` — что добавлять дальше,
и `INTEGRATION/INTEGRATION_INTO_REPO_RU.md` — куда класть файлы в репозитории.
