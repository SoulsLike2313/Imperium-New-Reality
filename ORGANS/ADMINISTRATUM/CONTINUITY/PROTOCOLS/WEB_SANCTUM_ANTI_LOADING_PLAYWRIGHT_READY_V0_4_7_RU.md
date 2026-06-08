# Web Sanctum V0.4.7 — anti-loading / Playwright ready

Причина падения V0.4.6: runtime ReferenceError из-за отсутствующего VERSION в main.js.
В результате renderContour не завершался, contour оставался LOADING, а Playwright корректно ловил regress.

Фикс:
- VERSION явно объявлен;
- window.__SANCTUM_READY выставляется после renderAll;
- Playwright ждёт ready-state, а не угадывает тайминг;
- runtime port 8789, test port 8797;
- screenshot-прогон сохраняет owner-visible evidence.
