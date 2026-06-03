# Evidence Index Foundation V0.1 (RU)

## Что это
Первый базовый индекс доказательств NewGen для Mechanicus:
- SQLite база с FTS поиском;
- индекс по reports/receipts/cards/scope packs/role packs/contracts/templates;
- seeds по warning/error и связям task/commit.

## Что не входит
- UI/visual прототипы;
- LLM/cloud активация;
- индексация private/local external context;
- broad cleanup.

## Ключевые файлы
- `evidence_index.sqlite3`
- `evidence_index_schema_v0_1.sql`
- `evidence_index_manifest.json`
- `warning_error_patterns_v0_1.json`
- `example_queries_v0_1.json`
- `EVIDENCE_INDEX_PLAYBOOK_V0_1.md`

## Быстрый цикл
1. Запустить builder.
2. Запустить query runner.
3. Запустить checker и сверить отчеты в report-root.
