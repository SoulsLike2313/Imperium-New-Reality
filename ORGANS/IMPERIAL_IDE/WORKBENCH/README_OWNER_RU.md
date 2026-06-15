# IMPERIAL IDE :: MECHANICUS WORKBENCH — V0.1
### Purple Dark Nebula Metallic · Warhammer Imperium style

Это управляемая оболочка над твоим уже существующим IMPERIAL_IDE контроль-шеллом
(коммит `f87ef9a`). Сделано так, чтобы ты запустил — и получил результат.

## Что внутри
- **GUI** (Python/Tkinter) — красивое окно: nebula-шапка, панели органов, стойка
  капсул Сервиторов, лог-консоль, диспетчер задач (round-robin).
- **TUI** (Python/ANSI) — тот же пульт в терминале, без зависимостей.
- **Капсулы Сервиторов** (Python + PowerShell-супервизор) — 2–3 Сервитора в
  изолированных процессах, round-robin, cooldown — чтобы лимиты не стопорили.
- **Мост в Механикус** (Python) — звонит твоему органному мосту, держит границу
  безопасности.
- **Тема** (TypeScript → JSON + PNG) — единый источник цветов для всех слоёв.
- **Нативная оболочка** (C#/WPF, опционально) — компилируемый `.exe`.

## Быстрый старт
```powershell
# GUI (основное окно)
pwsh ./run_imperial_workbench.ps1

# TUI в терминале
pwsh ./run_imperial_workbench.ps1 -Surface tui

# стойка капсул (2-3 Сервитора)
pwsh ./run_imperial_workbench.ps1 -Surface supervisor
```
Если PowerShell заблокирован политикой: `run_imperial_workbench.cmd gui`.

Привязка к репо: задай `IMPERIUM_ROOT` на корень `E:\IMPERIUM_NEW_GENERATION_NEW_REALITY`
— или положи пакет внутрь репо, он сам найдёт корень. Без репо работает в
SAMPLE-режиме (демо-данные), чтобы ты сразу увидел вид.

## Требования
- Python 3.10+ (Tkinter входит в стандартный Windows-инсталлятор).
- PowerShell 7+ желателен для супервизора (или Windows PowerShell 5.1).
- C#/WPF — только если собираешь нативный слой (см. NATIVE_CSHARP/README_BUILD_RU.md).

## Безопасность
- Всё по умолчанию в **dry-run**. Ничего не мутируется, ничего не пушится.
- Реальное выполнение заблокировано текущим governance; Workbench работает только read-only/dry-run.
  И только через органный мост Механикуса.
- Неизвестный инструмент → BLOCKED. Произвольный shell → запрещён.

## Карта файлов
```
GUI/        imperial_gui_workbench.py, sample_panels.json
TUI/        imperial_tui.py
SERVITORS/  servitor_capsule.py, servitor_capsule_supervisor.ps1, capsules.config.json, CAPSULE_MODEL_RU.md
BRIDGES/    mechanicus_workbench_bridge.py, mechanicus_integration_contract.json, sample_*.json, MECHANICUS_INTEGRATION_RU.md
THEME/      imperium_theme.json, imperium_theme.ts, nebula_background.png, THEME_NOTES_RU.md
NATIVE_CSHARP/  ImperialWorkbench.csproj, App/MainWindow/Theme (WPF), README_BUILD_RU.md
CONTRACTS/  LANGUAGE_RATIONALE_RU.md
VALIDATION/ validation_report.json
run_imperial_workbench.ps1 / .cmd, RUN_FIRST_RU.md
```

## Честный статус
См. `VALIDATION/validation_report.json`. Коротко: Python-файлы компилируются,
TUI проходит smoke. GUI/WPF/PowerShell НЕ запускались (нет дисплея/Windows в
песочнице) — запускай их у себя. Это кандидат, не канон.
