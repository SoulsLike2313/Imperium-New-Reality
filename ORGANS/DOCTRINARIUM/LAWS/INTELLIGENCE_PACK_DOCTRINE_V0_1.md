# Doctrinarium Law — Intelligence Pack Doctrine v0.1

## Закон

Default handoff/codebase context для Imperium не должен быть crude repo dump.

Default format:

1. manifest;
2. git truth;
3. tree index;
4. organ map;
5. tool passport index;
6. dependency edges;
7. SQLite-ready query index;
8. selected source slices;
9. owner summary.

## Запрещено как default

- полный repo snapshot без причины;
- raw evidence внутри source handoff;
- runtime/cache/test output;
- `.imperium_patch_backups/`;
- smoke vaults;
- nested archives без fixture/source manifest.

## Обоснование

Imperium должен улучшать внутренних агентов через лёгкое, быстро читаемое, индексируемое знание. Pack должен отвечать на вопросы: где сущность, кто владелец, какой lifecycle/risk, какие связи, какой passport, какой evidence lane.

## SQL/graph spine

`ATLAS_INDEX.sqlite` — первый локальный query layer. `DEPENDENCY_EDGES.jsonl` — первый graph-ready relation layer. Полноценный Atlas SQLite/Graph spine допускается как следующий patch после стабилизации Intelligence Pack Builder.
