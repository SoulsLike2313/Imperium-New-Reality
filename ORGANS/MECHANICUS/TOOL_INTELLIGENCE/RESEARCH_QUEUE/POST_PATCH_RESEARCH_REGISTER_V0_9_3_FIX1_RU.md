# Post Patch Research Register v0.9.3-FIX1

Тема: owner-facing metric integrity для Trinity Plus смотровых.

Вывод: визуальная смотровая является частью доказательства патча, поэтому проценты и progress bars должны хранить machine-readable ratio/denominator и отображаемый percent отдельно. Это снижает риск красивой, но неверной панели.

Рекомендация Mechanicus: для следующих dashboards добавить общую библиотеку metric helpers: `safe_ratio`, `safe_percent`, `bar_width`, `denominator_source`.
