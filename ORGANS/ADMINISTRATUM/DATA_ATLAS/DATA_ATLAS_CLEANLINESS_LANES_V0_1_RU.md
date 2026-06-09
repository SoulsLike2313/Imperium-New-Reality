# Data Atlas Cleanliness Lanes v0.1

Цель: превратить первичный список файлов в owner-visible линии очистки.

## Что добавлено

- cleanup lanes: source runtime leaks, git dirty review, archive lifecycle review, duplicate review, legacy quarantine review, passports needed, unknown semantics;
- owner-readable passport digest вместо сырой JSON-стены;
- рекомендации RU/EN для каждой сущности;
- исправление подсчёта skipped heavy dirs, чтобы счётчик не раздувался при обходе дерева;
- увеличение UI scan limit до 15000, чтобы поиск видел полный репозиторный индекс текущего размера.

## Правило безопасности

Это всё ещё read-only слой. Никакого delete/move/archive apply. Очистка начинается только следующим отдельным cleanup-gate после owner review.
