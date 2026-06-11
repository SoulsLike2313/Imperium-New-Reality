# Inquisition Evidence Seal Gate V0.1

Инквизиция считает evidence незавершённым, если после patch-run осталась только россыпь файлов без sealed pack.

Gate states:

- PASS: sealed pack exists, manifest exists, index entry exists.
- PASS_WITH_BUFFER_RETAINED: sealed pack exists, raw buffer intentionally retained.
- WARN_UNSEALED_BUFFER: buffer has files, but no pack exists.
- BLOCK_DELETE_WITHOUT_SEAL: попытка удалить raw buffer до seal.

Первый режим эксплуатации: sealer создаёт pack, но не удаляет buffer автоматически.

## V0.8.9.2 — Sealer Output-Root Contract

Новый gate закрывает дефект destructive seal режима: итоговый отчёт sealer-а не может писаться внутрь `HOT_BUFFER`, если одновременно включён `--delete-buffer-after-seal`.

Дополнительные gate states:

- `PASS_OUTPUT_ROOT_CONTRACT`: final report root переживает текущий режим seal.
- `WARN_NON_CANONICAL_SEALER_REPORT_ROOT`: final report root не внутри удаляемого buffer, но лучше перенести его в sealed pack folder или `$VAULT/logs/sealer`.
- `BLOCK_UNSAFE_SEALER_REPORT_ROOT`: `--delete-buffer-after-seal` + `--out-root` внутри удаляемого buffer. Seal/delete должен быть остановлен до записи/удаления.
- `PASS_SEALED_PACK_HEALTH`: `EVIDENCE_PACK.zip`, manifest, machine index, owner summary и SHA256 согласованы.
- `FAIL_SEALED_PACK_HEALTH`: sidecar отсутствует или hash не совпадает.

Правило: отчёт, который доказывает seal, не должен жить в области, которую seal удаляет.
