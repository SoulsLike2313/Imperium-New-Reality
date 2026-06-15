# Как интегрировать WARP в IDE / Механикус / ядро

## 1. Где физически лежит WARP
Положи пакет рядом с IDE, например:
```
ORGANS/IMPERIAL_IDE/WARP/        <- сюда ENGINE/LAUNCHER/UI
WARP/runtime/<session>/          <- рантайм сессий (в .gitignore!)
```
Добавь в `.gitignore`: `WARP/runtime/` — рантайм-грязь НЕ попадает в ядро/git.

## 2. Два пути входа в зону (обязательный лаунчер)
### Авто — когда стартует задача
В хук старта задачи (Astronomicon/IDE) вызови:
```python
from warp_autostart_hook import open_for_task
manifest = open_for_task(task_descriptor, trigger="auto",
                         core_root=r"E:\IMPERIUM_NEW_GENERATION_NEW_REALITY")
```
### Ручной — кнопкой WARP
Кнопка уже встроена в `UI/warp_gui_panel.py` («▶ ENTER WARP»). Либо из PowerShell:
```powershell
pwsh ./LAUNCHER/warp_launcher.ps1 -Task "собрать дашборд" -Kind THIRD_PARTY
```

## 3. Встраивание в Imperial IDE Workbench (GUI)
В воркбенче (предыдущий пакет) добавь панель WARP как вкладку/колонку:
```python
import sys; sys.path.insert(0, "WARP/UI")
from warp_gui_panel import WarpPanel
warp = WarpPanel(parent_frame, core_root=IMPERIUM_ROOT).pack(fill="both", expand=True)
# при старте задачи из IDE:
warp.open_for_task({"task": name, "kind": "CORE_CHANGE"}, trigger="auto")
```
Добавь панель `12 ◆ Servitor Capsules` соседом новую `13 ⊕ WARP Zone`.

## 4. Связь с Механикусом
- Инструменты органов вызываются внутри WARP через mechanicus bridge (dry-run
  по умолчанию). Неизвестный инструмент → BLOCKED.
- Результаты вызовов идут в метрики сессии (`record_metric`) с уровнем
  доказательств (E3 за реальный запуск, E4 за стабильный повтор).
- При RELEASE в CORE-зону release_manifest идёт в Механикус как заявка на
  продвижение (MOVE_DELETE_APPROVAL_GATE), а не прямая запись.

## 5. Связь с ядром (изоляция)
- Ядро = `core_root` (напр. `E:\IMPERIUM_NEW_GENERATION_NEW_REALITY`). Читается
  только как baseline для дифов (`warp_overlay.baseline_text`).
- Записи идут исключительно в `artifacts/`. Пути классифицируются по зонам
  (CORE/GOVERNANCE/SUPPORT/RUNTIME/UNKNOWN) в `warp_overlay.classify_zone`.
- Настрой зоны под своё дерево: правь `DEFAULT_ZONE_RULES` или передай
  свои глобы.

## 6. Порядок работы из IDE (коротко)
```
задача → [авто/кнопка] open warp → регистрация участников →
план+критерии → build (в artifacts) → метрики → gate →
  RELEASE → release_manifest → одобрение владельца → промоут в ядро
  HOLD    → доработка в WARP
  DISCARD → отбраковка, ядро чисто
```
