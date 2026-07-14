# IMPERIUM_PHASE6_REGISTRY_RUNTIME_TRANSITION_PROOF_0006

Этот пакет не меняет код Phase 6 и не требует нового клика.

Он доказывает, что единственная tracked-мутация после второго живого запуска:
`CAPABILITY_REGISTRY.json`.

Разрешены строго три семантических изменения:

1. `CORE_DIAGNOSTIC.last_validation.evidence_id`
2. `CORE_DIAGNOSTIC.last_validation.timestamp_utc`
3. `registry_digest`, корректно пересчитанный из всего документа

Все остальные поля registry должны быть тождественны версии из committed HEAD
`5da51c51199f759d4dbe04d15249f137f56dc27c`.

После независимой проверки перехода пакет запускает уже committed Python verifier,
который проверяет evidence, hashes, pinned Git/Pwsh, snapshot, Phase 3 и Reality.
