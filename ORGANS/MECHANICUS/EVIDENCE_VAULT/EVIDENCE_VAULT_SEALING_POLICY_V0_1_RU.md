# Evidence Vault Sealing Policy V0.1

Evidence не считается закрытым, пока он лежит россыпью в buffer/reports/json/csv/screenshots.

Каноническая форма завершённого evidence:

- `EVIDENCE_PACK.zip`
- `EVIDENCE_MANIFEST.json`
- `MACHINE_INDEX.json`
- `OWNER_SUMMARY_RU.md`
- `SHA256SUMS.txt`
- запись в `indexes/evidence_pack_index.jsonl`

Правила:

1. `HOT_BUFFER` — только временная рабочая зона patch-run.
2. `SEALED_PACK` — канонический пакет evidence.
3. Raw buffer удаляется только после seal и только по явному флагу.
4. Source repo никогда не является evidence dump.
5. `_LOCAL_HANDOFF` не является вечным архивом.
6. Data Atlas должен видеть sealed pack как сущность, а не россыпь файлов.
