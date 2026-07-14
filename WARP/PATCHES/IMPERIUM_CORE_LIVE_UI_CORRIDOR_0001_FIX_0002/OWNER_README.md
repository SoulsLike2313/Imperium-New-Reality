# IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002

Узкая Phase 6 коррекция после точной разведки.

Ключевой инвариант: в `service.py` сохраняется буквальный маршрут `return self.execute_demo()`, на котором Phase 3 доказывает registry + typed executor + Owner gate.

Пакет не добавляет Tauri-команд и не создаёт отдельного writer API. Уникальный UI correlation context передаётся внутри существующего `corridor_ui_action`; evidence сохраняется существующим `EvidenceStore` после `execute_capability`.

## Запуск

`pwsh WARP/PATCHES/IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002/RUN_IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002.ps1`

После baseline: запустить приложение, нажать **Run Diagnostic** один раз, затем **Refresh** один раз, закрыть приложение.

## Проверка

`pwsh WARP/PATCHES/IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002/VERIFY_IMPERIUM_CORE_LIVE_UI_CORRIDOR_0001_FIX_0002.ps1`

Ожидаемый verdict: `LIVE_UI_CORRIDOR_PROVEN`.
