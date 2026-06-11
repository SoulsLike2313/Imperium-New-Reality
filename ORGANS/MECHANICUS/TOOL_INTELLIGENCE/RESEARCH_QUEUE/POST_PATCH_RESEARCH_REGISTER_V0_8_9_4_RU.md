# Post-Patch Research Register — v0.8.9.4

## Тема

Intelligence Pack Receipt / Final Digest Contract.

## Что берём в Imperium

- SQLite остаётся application-file/index spine для переносимого локального query layer.
- SLSA/provenance подход берём как вдохновение: artifact должен иметь внешнюю attestable receipt/provenance запись.
- W3C Data Integrity берём как направление будущего: structured document integrity через hash/proof outside the mutable payload.

## Решение

В v0.8.9.4 не вводим криптографические подписи. Вводим минимальный durable receipt contract:

```text
ZIP + FINAL_SHA256SUMS + MACHINE_RECEIPT + sidecar manifest + owner summary
```

Подписи/attestations — отдельный будущий capability candidate.
