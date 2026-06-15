# Data Atlas — Repo Hygiene Board v0.1

Назначение: дать owner-у и агентам видимую карту грязи в репозитории до любых destructive действий.

## Что показывает board

- сколько файлов просканировано;
- сколько файлов попало в action/review lanes;
- распределение по органам;
- распределение по file kinds;
- очереди: `PASSPORT_REQUIRED`, `PACK_TO_VAULT_CANDIDATE`, `FIXTURE_MANIFEST_REQUIRED`, `OWNER_REVIEW_MOVE`, `SAFE_RUNTIME_DELETE`, `KEEP_SOURCE`;
- путь к SQLite индексу классификации.

## Правило owner-facing отображения

Data Atlas не удаляет и не переносит файлы. Он показывает карту, lane, причину и следующий безопасный шаг.

## Следующий уровень

После Batch 001 board должен стать входом для Evidence Vault Migration Batch и Mechanicus passporting queue.
