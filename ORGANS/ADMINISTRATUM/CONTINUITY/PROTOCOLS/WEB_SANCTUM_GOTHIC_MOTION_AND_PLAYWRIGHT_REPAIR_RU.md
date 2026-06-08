# Web Sanctum V0.4.7 — gothic motion / Playwright repair

Причина hotfix: V0.4.4 визуально принят как направление, но Playwright мог цепляться за уже запущенный static server на 8789 и видеть `LOADING`, а `/api/health` отдавал 404. В V0.4.7 тесты используют dedicated port 8797 и `reuseExistingServer: false`.

Визуальный слой усилен: gothic frame, brass/copper accents, forge band, gear halo, richer panels, filled Mechanicus surface. Стиль остаётся Imperium dark/gold/violet, добавки — steampunk/gothic.

Safety: нет arbitrary shell endpoint, нет live LLM, нет live servitor execution, нет trading execution. Local actions остаются allowlisted и включаются только через `RUN_WEB_SANCTUM_ACTIONS.ps1`.
