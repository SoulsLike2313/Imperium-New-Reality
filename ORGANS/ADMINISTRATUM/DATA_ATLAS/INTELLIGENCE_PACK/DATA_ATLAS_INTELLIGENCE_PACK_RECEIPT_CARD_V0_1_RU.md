# Data Atlas Card — Intelligence Pack Receipt Contract v0.1

## Назначение

Карточка показывает, что Intelligence Pack закрыт не самоссылочным hash внутри ZIP, а sidecar receipt рядом с ZIP.

## Health fields

- `zip_exists`
- `final_sha256sums_exists`
- `machine_receipt_exists`
- `sidecar_manifest_exists`
- `owner_summary_exists`
- `actual_zip_sha256_matches_receipt`
- `embedded_manifest_has_no_final_zip_sha256`
- `embedded_manifest_digest_matches_sidecar`

## Owner rule

Intelligence Pack считается пригодным для handoff только если рядом с ZIP есть sidecar closure:

```text
<pack_id>.zip
<pack_id>.INTELLIGENCE_PACK_MANIFEST.json
<pack_id>.FINAL_SHA256SUMS.txt
<pack_id>.MACHINE_RECEIPT.json
<pack_id>.OWNER_SUMMARY_RU.md
```

Final ZIP SHA256 нельзя хранить внутри `MANIFEST.json` внутри ZIP: запись hash внутрь архива меняет архив и ломает hash.
