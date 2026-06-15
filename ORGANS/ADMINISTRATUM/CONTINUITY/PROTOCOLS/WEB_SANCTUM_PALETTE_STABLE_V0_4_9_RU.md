# Web Sanctum V0.4.9 — Playwright palette stable evidence

Назначение: закрыть остаточный Playwright fail после V0.4.8.

Причина: тест нажимал Enter в command palette, но runtime не обрабатывал Enter как выбор первого результата.

Исправление:
- добавлен executeFirstPaletteItem() в main.js;
- Enter в открытой command palette выполняет первый отфильтрованный пункт;
- тест проверяет, что первый результат содержит Mechanicus, затем нажимает Enter;
- test:pw:report переведён на порт 9330, добавлен alt 9331 на случай занятого 9323;
- screenshots остаются owner-visible evidence.

Safety: no arbitrary shell, no live LLM, no servitor execution, no trading execution.
