# Data Atlas — Hygiene Batch Preview Card v0.1

Назначение: показать owner-у первый batch наведения порядка до любых действий с source.

## Что видит карта

- target organ: `REPORTS_LEGACY`
- target lane: `PACK_TO_VAULT_CANDIDATE`
- candidate count и общий размер
- top folders и риск-распределение
- owner gate: preview не равен execution
- Trinity Plus proof: HTML + terminal + markdown + machine JSON

## Закон

Batch preview разрешает только планирование и ревью. Упаковка в Evidence Vault, перемещение или удаление source требуют отдельного owner-approved execution patch.
