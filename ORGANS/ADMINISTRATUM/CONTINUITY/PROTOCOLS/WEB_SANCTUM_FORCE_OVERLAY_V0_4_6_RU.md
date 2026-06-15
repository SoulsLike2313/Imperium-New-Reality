# Web Sanctum force overlay V0.4.7

Цель: остановить stale-запуск V0.4.4 и жёстко заменить рабочую папку `ORGANS/IMPERIAL_IDE/WEB_SANCTUM` на актуальный anti-loading force-overlay.

Причина: V0.4.5 мог не лечь поверх старого WEB_SANCTUM или пользователь запускал уже поднятый старый server/report. Симптомы: package name `imperium-web-sanctum-v044`, нет `test:pw:screenshots`, contour остаётся `LOADING`.

V0.4.7:
- полностью заменяет WEB_SANCTUM, не пытаясь мягко сливать старые файлы;
- добавляет `id="contour"` вместе с `data-testid="contour"`;
- меняет runtime port на 8789, чтобы не путаться со старым 8787;
- меняет Playwright test port на 8797;
- добавляет self-check в `web_sanctum_smoke.py`;
- усиливает gothic/steampunk density без слома Imperium dark/gold/violet стиля;
- сохраняет no arbitrary shell / no live LLM / no servitor execution / no trading execution.
