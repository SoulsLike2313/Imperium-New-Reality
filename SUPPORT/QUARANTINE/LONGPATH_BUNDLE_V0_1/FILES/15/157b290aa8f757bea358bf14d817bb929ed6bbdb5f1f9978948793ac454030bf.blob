# Inquisition Evidence Seal Gate V0.1

Инквизиция считает evidence незавершённым, если после patch-run осталась только россыпь файлов без sealed pack.

Gate states:

- PASS: sealed pack exists, manifest exists, index entry exists.
- PASS_WITH_BUFFER_RETAINED: sealed pack exists, raw buffer intentionally retained.
- WARN_UNSEALED_BUFFER: buffer has files, but no pack exists.
- BLOCK_DELETE_WITHOUT_SEAL: попытка удалить raw buffer до seal.

Первый режим эксплуатации: sealer создаёт pack, но не удаляет buffer автоматически.
