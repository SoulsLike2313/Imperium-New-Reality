# Post-Patch Research Register — v0.9.0 Repo Hygiene Classification Batch 001

## Что зарегистрировать через Mechanicus

- `inquisition.repo_hygiene_classifier` как read-only source classifier.
- будущий `mechanicus.evidence_vault_migration_batch_runner` только после owner gate.
- будущий `mechanicus.fixture_manifest_writer` для fixture/source exceptions.
- будущий `mechanicus.tool_passport_backfill_assistant` для PASSPORT_REQUIRED lane.

## Архитектурные ориентиры

- OpenLineage: модель run/job/dataset/facets как вдохновение для lineage-событий и atomic metadata facets.
- DataHub/OpenMetadata: catalog/governance/lineage/ownership как ориентир для Data Atlas.
- Great Expectations: validation/expectation mindset как ориентир для hygiene gates.

## Решение

Batch 001 не удаляет. Он строит классификацию, SQLite индекс и очереди lane-действий.
