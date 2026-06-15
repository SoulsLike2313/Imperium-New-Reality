# Post-Patch Research Register — v0.8.9.3 Intelligence Pack Builder

## Что регистрируем через Mechanicus

- `mechanicus.imperium_intelligence_pack_builder`
- `inquisition.intelligence_pack_hygiene_gate`

## Что вносим в doctrine

- Crude repo dump не является default handoff.
- Default context pack = manifest/indexes/edges/sqlite/slices/owner summary.
- Evidence читается через Evidence Vault manifest/index, а не копируется в source handoff.

## Архитектуры для вдохновения

- SQLite application file format: локальный переносимый queryable index.
- DuckDB: будущая аналитика по большим индексам/логам, если SQLite станет узким местом.
- GraphRAG: graph edges/community summaries как образ будущего Graph Atlas, без включения live LLM backend.
- DataHub: ownership, discovery, governance, observability, lineage как образ зрелого Data Atlas.

## Следующий research gate

После v0.8.9.3 проверить: нужно ли повышать `ATLAS_INDEX.sqlite` из pack artifact до постоянного Data Atlas SQLite spine.
