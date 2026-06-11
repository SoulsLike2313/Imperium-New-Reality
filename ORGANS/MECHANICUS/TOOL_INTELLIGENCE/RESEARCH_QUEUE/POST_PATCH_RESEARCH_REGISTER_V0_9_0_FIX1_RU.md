# Post Patch Research Register — v0.9.0-FIX1 Trinity Plus

## Что зарегистрировано

Патч вводит `Trinity Plus`: обязательную owner-facing смотровую часть для patch packs, где владелец видит, что реально добавилось и работает.

## Внешние ориентиры

- Rich: terminal tables/panels/pretty output как направление для будущей rich-смотровой.
- Textual: TUI/terminal app как возможная эволюция Warp cockpit.
- Streamlit: быстрые локальные data apps/dashboard как возможный web-путь для owner boards.

## Решение сейчас

Не добавлять внешние зависимости. Первый visual proof реализован на стандартной библиотеке Python: terminal text + markdown + static HTML + machine JSON.

## Следующий gate

Если owner примет Trinity Plus, будущие крупные patch packs должны явно указывать:

- `TRINITY_ONLY` — архитектурный patch без смотровой;
- `TRINITY_PLUS` — patch требует visual proof surface.
