# Inquisition Evidence Write Guard V0.1

Инквизиция проверяет не только грязь внутри source repo, но и саму дисциплину записи evidence.

## Законы

1. Source repo не является evidence-хранилищем.
2. Raw evidence живёт только в HOT_BUFFER и только до seal.
3. После seal остаются pack + manifest + summary + index.
4. TTL не удаляет source repo.
5. Quarantine не равен deletion.
6. Protected registry не считается мусором.
7. Purge выполняется только отдельным gate.

## Что блокируется

- screenshots/playwright reports/test results в source;
- cache/runtime в source;
- unknown write roots;
- unsealed buffers старше TTL;
- большие архивы без lifecycle.

## Что не блокируется автоматически

- source fixtures с явным lifecycle;
- pinned evidence packs;
- protected runtime registries;
- owner-reviewed archives.
