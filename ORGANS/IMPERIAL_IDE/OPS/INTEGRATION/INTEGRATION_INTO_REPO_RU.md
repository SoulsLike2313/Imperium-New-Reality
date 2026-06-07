# ИНТЕГРАЦИЯ В РЕПОЗИТОРИЙ (RU)

Репозиторий: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY` (ветка master).
Статус: `CANDIDATE_NOT_CANON`. Сначала smoke, потом решение владельца.

## 1. Куда класть файлы

Распакуйте содержимое `ENGINE/`, `CLI/`, `TUI/`, `TESTS/` в:

```
ORGANS/IMPERIAL_IDE/OPS/
    imperium_ops/      <- из ENGINE/imperium_ops/
    CLI/               <- из CLI/
    TUI/               <- из TUI/
    TESTS/             <- из TESTS/
```

Лаунчеры — в корень органа IDE:

```
ORGANS/IMPERIAL_IDE/run_imperial_ide_ops.ps1
ORGANS/IMPERIAL_IDE/run_ops_smoke.ps1
```

GUI-панели (следующий этап) — в `ORGANS/IMPERIAL_IDE/PANELS/*_panel.py`,
импортируя ядро:

```python
import os, sys
OPS = os.path.join(os.environ["IMPERIUM_ROOT"], "ORGANS", "IMPERIAL_IDE", "OPS")
sys.path.insert(0, OPS)
from imperium_ops import lifecycle, task_console  # и т.д.
```

## 2. Проверка после распаковки (обязательно)

```powershell
$env:IMPERIUM_ROOT = "E:\IMPERIUM_NEW_GENERATION_NEW_REALITY"
python -m py_compile (Get-ChildItem -Recurse -Filter *.py ORGANS\IMPERIAL_IDE\OPS).FullName
python ORGANS\IMPERIAL_IDE\OPS\TESTS\ops_smoke.py   # ожидаем SMOKE RESULT: PASS
```

## 3. Куда пишутся результаты (dry-run)

- Таскпаки: `ORGANS/IMPERIAL_IDE/OPS/STAGING/TASKPACKS/<task_id>/EXTRACTED/`
- Регистрация: `ORGANS/IMPERIAL_IDE/OPS/STAGING/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/<task_id>/`
- Отчёты: `ORGANS/IMPERIAL_IDE/OPS/STAGING/REPORTS/<task_id>/lifecycle_report.json` + `RECEIPTS/`

Kernel-дерево **не трогается**, пока не сняты dry-run и safety-флаги.

## 4. Связь с уже живыми модулями (commit 1fbe694 / V0_2)

- `METAOS/ENGINE/administratum_bundle_gate.py` — этап 11 lifecycle соответствует
  его RELEASED/HELD-логике (можно позже вызывать напрямую).
- `WORKBENCH/BRIDGES/mechanicus_workbench_bridge.py` — этап 4 (policy check).
- `PANELS/{metaos_panel.py,warp_panel.py}` — сюда же добавятся
  task_console_panel / astronomicon_panel / git_closure_panel.

## 5. Рекомендуемый порядок commit

1. Распаковать в `ORGANS/IMPERIAL_IDE/OPS/` + лаунчеры.
2. Прогнать py_compile + ops_smoke → PASS.
3. `git add ORGANS/IMPERIAL_IDE/OPS ORGANS/IMPERIAL_IDE/run_*ops*.ps1`
4. commit: `TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-...-PC-V0_1: operational engine (dry-run)`
5. push — только после scope-check + secret-check (встроены в `git_closure`).
