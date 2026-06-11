# Post-Patch Research Register — v0.9.2

Тема: owner-gated hygiene batch preview.

## Внешние ориентиры

- OpenLineage: events/facets как образ для того, чтобы batch preview фиксировал run/job/dataset context и был расширяемым через facets.
- DataHub: lineage/ownership как ориентир для Data Atlas — кандидаты должны иметь owner, lineage и governance context.
- OpenMetadata: discovery/governance/lineage как ориентир для будущей owner-review навигации по hygiene assets.
- Great Expectations: явные expectations/validations как образ для PASS/FAIL gates и reproducible validation docs.

## Что регистрировать дальше через Mechanicus

- Evidence Vault Batch Executor, но только после owner gate.
- Fixture Manifest Generator для lane `FIXTURE_MANIFEST_REQUIRED`.
- Passport Batch Generator для lane `PASSPORT_REQUIRED`.
- Rich/Textual terminal renderer для более удобного операционного терминала.
