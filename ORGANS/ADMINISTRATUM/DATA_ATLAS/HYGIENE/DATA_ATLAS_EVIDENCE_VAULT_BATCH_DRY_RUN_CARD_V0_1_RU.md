# Data Atlas Card — Evidence Vault Batch 001 Dry-run v0.1

Trinity Plus слой для проверки готовности Batch 001 к будущей упаковке в Evidence Vault.

## Что показывает

- сколько кандидатов из pack plan существует в source;
- сколько файлов missing;
- сколько SHA256 совпадает с планом;
- какой объём будет подготовлен к упаковке;
- какой staging layout будет использован будущим execution-патчем;
- что source deletion остаётся заблокированным.

## Safety

Dry-run не копирует, не перемещает, не удаляет и не создаёт Vault pack. Он создаёт только смотровую и машинные отчёты во внешнем `--out-root`.
