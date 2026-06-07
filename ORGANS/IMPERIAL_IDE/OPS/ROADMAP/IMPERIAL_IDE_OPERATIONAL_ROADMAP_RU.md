# IMPERIAL IDE :: OPERATIONAL ROADMAP (RU)

Цель: довести IDE до состояния, когда владелец ставит и закрывает задачи
**изнутри IDE**, без ручных ZIP.

## Статус по пунктам "минимального рабочего v1" (раздел 11 требований)

| # | Требование | Статус в этом пакете |
|---|---|---|
| 1 | GUI opens reliably | Позже (GUI-панели = след. этап) |
| 2 | TUI opens reliably | ГОТОВО — `TUI/imperial_ide_ops_tui.py` |
| 3 | Repo root auto-detected | ГОТОВО — `IMPERIUM_ROOT`/cwd |
| 4 | Dashboard shows live repo state | ГОТОВО — TUI dashboard |
| 5 | Task Console creates taskpack | ГОТОВО — `task_console` + `taskpack_builder` |
| 6 | Astronomicon registration from IDE | ГОТОВО — `astronomicon_register` (dry-run) |
| 7 | Launch card shown in IDE | ГОТОВО — `launch_card` |
| 8 | Reports browser | ЧАСТИЧНО — отчёты пишутся в ORGANS/IMPERIAL_IDE/OPS/STAGING/REPORTS |
| 9 | Receipts browser | ЧАСТИЧНО — `receipts.validate_receipt` |
| 10 | Mechanicus tools/capabilities visible | Позже (подключить реестры) |
| 11 | Dry-run tool invocation | Позже (интерфейс готов) |
| 12 | WARP session can be created | Позже (стыковка с WARP_ZONE) |
| 13 | MetaOS route preview | ГОТОВО (этап 3 lifecycle, preview) |
| 14 | Administratum bundle gate smoke | ГОТОВО — этап 11 lifecycle |
| 15 | Validation center | ГОТОВО — этап 9 + receipts |
| 16 | Commit/push closure tracked | ГОТОВО — `git_closure` (gated) |
| 17 | Safety center blocks unsafe execution | ГОТОВО — `safety_gate` |
| 18 | Extensions listed/validated | Позже (Extension Manager) |
| 19 | Owner runs one full task in IDE | ГОТОВО — `lifecycle.run_lifecycle` + CLI/TUI |

## Этапы после этого пакета

1. **GUI-панели** (раздел 2.1–2.14): добавить `PANELS/*_panel.py`, которые
   импортируют это ядро через `sys.path.insert(0, OPS)`.
2. **Mechanicus live registry**: подключить `ORGANS/MECHANICUS/REGISTRY/*.json`.
3. **WARP session bridge**: связать lifecycle этап 8 с WARP_ZONE.
4. **Real Servitor/LLM**: provider registry, cost profile, escalation — только
   после `AllowReal` gate и явного provider config.
5. **Extension Manager** + **Product Workspaces** (article/app/game/music/...).
6. **Controlled editing**: сначала read/view/control, потом редактирование файлов.

## Следующий крупный task

```
TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-TASK-CONSOLE-AND-TASKPACK-BUILDER-PC-V0_1
```

Этот пакет и есть его ядро: Task Console, Taskpack Builder, Astronomicon
registration, Launch Card, Servitor handoff, MetaOS route preview, Reports/
Receipts tracking, Git closure. GUI-обёртка навешивается сверху.
