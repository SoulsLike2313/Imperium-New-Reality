# Doctrinarium Law — Repo Hygiene Lane Doctrine v0.1

## Закон

Imperium не чистит source по ощущению. Любое действие над грязью проходит через lane.

## Lanes

- `KEEP_SOURCE`: источник остаётся как есть.
- `PASSPORT_REQUIRED`: tool-like файл должен получить Mechanicus passport.
- `PACK_TO_VAULT_CANDIDATE`: evidence/report/archive сначала копируется или пакуется в Evidence Vault.
- `FIXTURE_MANIFEST_REQUIRED`: fixture остаётся в source только с manifest/source exception.
- `OWNER_REVIEW_MOVE`: требуется ручное решение owner-а.
- `SAFE_RUNTIME_DELETE`: runtime/cache/local-only мусор можно удалять только через explicit gate.

## Запрет

Нельзя автоматически удалять source evidence, screenshots, reports, archives или fixtures без manifest, receipt и owner gate.

## Архитектурный смысл

Классификация должна быть queryable: JSONL для очередей, SQLite для запросов, Data Atlas board для owner-а, graph edges для будущего Graph Atlas.
