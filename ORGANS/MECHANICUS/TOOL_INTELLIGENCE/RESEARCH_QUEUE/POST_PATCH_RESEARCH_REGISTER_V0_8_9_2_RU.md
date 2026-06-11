# Post-Patch Research Register — v0.8.9.2

Цель: после патча не просто закрыть баг, а усилить архитектурную память Imperium.

## Что зарегистрировать через Mechanicus следующим проходом

- `imperium_intelligence_pack_builder` — лёгкий pack: manifests, indexes, dependency edges, selected source slices вместо full repo dump.
- `atlas_sqlite_index_builder` — локальный SQLite индекс по files/tools/organs/evidence/findings/passports.
- `graph_edge_exporter` — JSONL/SQLite edges: `file -> organ`, `tool -> passport`, `finding -> risk`, `evidence_pack -> patch`, `patch -> doctrine`.
- `evidence_vault_health_checker` — health-check sealed pack без распаковки ZIP.
- `post_patch_research_register` — обязательный closure pass после каждого patch-pack.

## Внешние архитектурные ориентиры

- SQLite application file format: не таскать pile-of-files, когда нужен переносимый queryable local truth.
- DuckDB: локальная аналитика по индексам/логам/таблицам без отдельного сервера.
- GraphRAG: knowledge graph + community summaries как образ будущего Graph Atlas.
- DataHub: data catalog / ownership / governance / observability / lineage как ориентир для Data Atlas.

## Что внесено в doctrine

`ORGANS/DOCTRINARIUM/LAWS/STORAGE_INDEX_GRAPH_DOCTRINE_V0_1.md`

Главное правило: packs are transport; indexes are memory.

## Как этот патч улучшает внутренних агентов

- Mechanicus лучше понимает опасные write roots sealer-а.
- Inquisition получает read-only gate против unsafe destructive seal.
- Data Atlas получает карточку sealed pack health.
- Doctrinarium получает storage/index/graph закон для будущих patch-pack.
