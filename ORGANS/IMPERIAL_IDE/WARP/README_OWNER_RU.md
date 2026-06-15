# IMPERIUM WARP ZONE V0.1 — читать владельцу

## Что это
WARP — горячая зона разработки внутри IDE. Любая работа (правка ядра,
силы Империума, стороннее ПО) идёт только внутри зоны. Ядро живёт
отдельно и не загрязняется. Продукт выходит только через шлюз (GATE).

## Структура пакета
```
ENGINE/      ядро движка: летопись, изоляция/дифы, шлюз, сессия
  warp_eventlog.py    append-only JSONL летопись
  warp_overlay.py     классификация зон + unified diff против ядра
  warp_gate.py        вердикт RELEASE/HOLD/DISCARD + анти fake-green
  warp_zone.py        главный движок WarpSession
LAUNCHER/    вход в зону
  warp_launcher.py        CLI (open/status/gate/list/discard)
  warp_autostart_hook.py  авто-открытие при старте задачи
  warp_launcher.ps1       PowerShell-лаунчер
UI/          визуализация
  warp_tui.py        текстовый вид зоны (стадии/дифы/метрики)
  warp_gui_panel.py  Tkinter-панель + кнопка WARP
CONTRACTS/   JSON-контракты (зона, критерии, шлюзы)
DOCS/        доктрина, жизненный цикл, интеграция, критерии, дорожная карта
SAMPLE/      пример task descriptor
VALIDATION/  честный отчёт проверки
warp_smoke.py          end-to-end демо (DISCARD и RELEASE)
```

## Быстрый старт
См. `RUN_FIRST_RU.md`.

## Статус
CANDIDATE_NOT_CANON. Это инженерная форма, а не канон. Канонизация — по
твоему решению (OD-CANON) после проверки на живом PC.
