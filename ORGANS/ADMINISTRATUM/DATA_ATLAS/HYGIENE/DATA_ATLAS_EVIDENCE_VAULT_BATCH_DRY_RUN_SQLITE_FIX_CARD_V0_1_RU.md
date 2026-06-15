# Data Atlas — Evidence Vault Batch Dry-Run SQLite Fix v0.1

Patch: `v0.9.4-FIX1`
Surface: `EVIDENCE_VAULT_BATCH_DRY_RUN_SQLITE_FIX_CARD_V0_1`

## Что исправлено

Dry-run executor v0.9.4 падал на SQLite DDL: колонка `exists` конфликтовала с SQL keyword `EXISTS` в `CREATE TABLE dry_run_items`.

Исправление:

- JSON/report key остаётся `exists` для совместимости с dry-run report;
- SQLite column переименована в `exists_on_disk`;
- executor version поднята до `0.1.1`;
- smoke должен доходить до `SMOKE PASS v0.9.4-FIX1`.

## Owner-facing статус

Это технический FIX1. Он не копирует, не перемещает, не удаляет и не упаковывает source. Он только делает dry-run proof пригодным для SQLite validation.
