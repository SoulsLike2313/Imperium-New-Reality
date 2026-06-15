# Data Atlas Card — Intelligence Pack v0.1

Назначение: показать owner-у и внутренним агентам, что handoff/codebase context больше не является crude repo dump.

## Что показывает карточка

- `repo_files_scanned`: сколько tracked файлов было прочитано как источник индекса.
- `source_slices_total`: сколько файлов реально включено как source slices.
- `dependency_edges_total`: сколько связей экспортировано в graph-ready `DEPENDENCY_EDGES.jsonl`.
- `sqlite_index`: наличие `ATLAS_INDEX.sqlite` как SQL-ready локального индекса.
- `forbidden_defaults`: что не должно попадать в default handoff.

## Owner-facing health states

- `PASS_INTELLIGENCE_PACK_BUILT`: pack собран builder-ом.
- `PASS_INTELLIGENCE_PACK_HYGIENE`: Inquisition gate подтвердил manifest/index/edges/sqlite и отсутствие root-local мусора.
- `FAIL_INTELLIGENCE_PACK_HYGIENE`: pack содержит forbidden/runtime/local-only content или потерял обязательные индексы.

## Архитектурный смысл

Data Atlas больше не должен требовать от Логоса читать 9000 файлов и 160 МБ архива. Нормальный вход в курс: manifest, tree index, organ map, graph edges, SQLite index и selected source slices.
