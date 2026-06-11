# Inquisition Evidence Migration Policy V0.1

Назначение: перевести старую evidence-грязь из режима "россыпь файлов" в режим owner-reviewed migration plan.

Закон:

1. Source repo не является evidence storage.
2. Evidence в source не удаляется автоматически.
3. Архивы, скриншоты, HTML/trace/HAR и runtime cache получают отдельные migration lanes.
4. Очевидный source cache (`__pycache__`, `.pyc`, `.pytest_cache`) может быть удалён только отдельным safe-cache gate.
5. Архивы и taskpack/evidence bundles сначала классифицируются: fixture, taskpack registry, vault migration, quarantine, owner-review.
6. Data Atlas показывает migration state, а Inquisition запрещает новую грязь без классификации.

Основные lanes:

- `PACK_TO_VAULT_CANDIDATE` — кандидат на упаковку в Evidence Vault pack.
- `OWNER_REVIEW_MOVE` — перенос только owner-reviewed patch.
- `OWNER_REVIEW_CLASSIFY` — нужен lifecycle decision.
- `FIXTURE_ALLOWED_NEEDS_MANIFEST` — fixture допустим, но нужен manifest/паспорт.
- `SAFE_CACHE_DELETE` — безопасный cache cleanup lane.
- `QUARANTINE_CANDIDATE` — убрать из активного дерева, но не уничтожать.
- `KEEP_SOURCE_REGISTER_FIXTURE` — оставить в source, но зарегистрировать как fixture/source asset.

Этот слой планирует миграцию, но не делает destructive cleanup по умолчанию.
