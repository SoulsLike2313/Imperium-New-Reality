# Data Atlas — Evidence Vault Batch 001 Receipt Registration v0.1

Назначение: связать `REPORTS_LEGACY / PACK_TO_VAULT` Batch 001 с проверенным Evidence Vault receipt.

Этот слой не чистит source. Он фиксирует факт, что внешний Vault pack существует, sidecars присутствуют, ZIP/hash/counts/SQLite проверены, а Data Atlas получил registration artifact.

Owner gate: регистрация разрешает только следующий cleanup proposal. Удаление/перемещение source запрещено без отдельного owner approval.
