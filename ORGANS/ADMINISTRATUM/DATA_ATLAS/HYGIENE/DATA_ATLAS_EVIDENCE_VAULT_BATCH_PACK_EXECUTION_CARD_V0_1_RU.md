# Data Atlas Card — Evidence Vault Batch 001 Pack Execution v0.1

## Назначение

Карточка фиксирует новый execution-шаг наведения порядка: Batch 001 `REPORTS_LEGACY / PACK_TO_VAULT` может быть скопирован и упакован в Evidence Vault без удаления source.

## Что считается успехом

- Все кандидаты найдены.
- SHA256 рассчитаны.
- `EVIDENCE_PACK.zip` создан в Evidence Vault.
- Рядом есть manifest, machine index, receipt, SHA256SUMS и Trinity Plus dashboard.
- Source не удалён, не перемещён, не переписан.

## Следующий gate

После execution требуется verification/registration patch: проверить sealed receipt, зарегистрировать pack в Data Atlas, потом отдельно строить source cleanup proposal.
