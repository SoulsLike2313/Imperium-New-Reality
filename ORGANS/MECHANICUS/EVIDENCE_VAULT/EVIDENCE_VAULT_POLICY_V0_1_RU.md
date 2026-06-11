# Evidence Vault Policy V0.1

Evidence Vault — это отдельный storage root для доказательств, скринов, отчётов, CSV/JSON/MD outputs и audit bundles.

Канонический root:

```text
E:\IMPERIUM_EVIDENCE_VAULT
```

## Структура

```text
buffer/active/<PATCH_ID>/raw
buffer/active/<PATCH_ID>/screenshots
buffer/active/<PATCH_ID>/json
buffer/active/<PATCH_ID>/csv
buffer/active/<PATCH_ID>/logs
buffer/active/<PATCH_ID>/reports
packs/YYYY/MM/<PATCH_ID>/EVIDENCE_PACK.zip
packs/YYYY/MM/<PATCH_ID>/EVIDENCE_MANIFEST.json
packs/YYYY/MM/<PATCH_ID>/OWNER_SUMMARY_RU.md
packs/YYYY/MM/<PATCH_ID>/MACHINE_INDEX.json
packs/YYYY/MM/<PATCH_ID>/SHA256SUMS.txt
indexes/evidence_pack_index.jsonl
indexes/latest_manifest.json
quarantine/YYYY/MM/<QUARANTINE_ID>
```

## Pack-after-patch rule

Каждый существенный patch-run должен завершаться seal evidence pack. Raw buffer после seal должен быть удалён или оставлен только при owner override.

## Delete rule

Удаление raw evidence происходит только после:

1. manifest created;
2. pack hash calculated;
3. index updated;
4. owner summary written;
5. Inquisition guard confirms pack exists.
