# Post Patch Research Register — v0.9.4-FIX1

## Исправление

Dry-run executor использовал SQLite column name `exists`. Это небезопасно для SQL DDL, потому что `EXISTS` является SQL keyword. Для машинных индексов Imperium вводится правило: поля SQLite не должны называться SQL keywords, даже если JSON keys их используют.

## Doctrine candidate

Добавить в storage/index doctrine:

- JSON может хранить owner-readable natural keys;
- SQL layer должен использовать safe column names;
- keyword-like поля переводить в явные имена: `exists_on_disk`, `is_file`, `source_delete_allowed`, etc.;
- smoke обязан открывать SQLite и проверять таблицы.
