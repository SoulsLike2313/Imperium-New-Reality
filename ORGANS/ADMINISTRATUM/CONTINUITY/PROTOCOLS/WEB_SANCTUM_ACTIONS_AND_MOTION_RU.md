# WEB SANCTUM ACTIONS AND MOTION V0.4.4

Этот протокол фиксирует разворот UI/UX на web renderer.

## Правило

Tk launcher остаётся fallback. Premium IDE развивается в `ORGANS/IMPERIAL_IDE/WEB_SANCTUM`.

## Действия

- Read-only запуск использует local bridge только для snapshot/health.
- Allowlisted actions запуск требует `RUN_WEB_SANCTUM_ACTIONS.ps1`.
- Нет произвольного shell endpoint.
- Разрешены только фиксированные owner-visible действия: smoke, TUI fallback, Tk fallback, открыть repo/continuity/reports, export snapshot.

## Acceptance

1. Визуально web renderer лучше Tk.
2. Анимации плавнее, frame pacing честно виден.
3. Ctrl+K command palette работает.
4. Playwright покрывает navigation/actions/read-only bridge.
5. H commit только после owner visual acceptance.
