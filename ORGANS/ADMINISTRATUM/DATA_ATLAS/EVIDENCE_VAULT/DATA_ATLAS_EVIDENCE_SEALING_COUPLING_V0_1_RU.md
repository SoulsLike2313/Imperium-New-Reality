# Data Atlas / Evidence Sealing Coupling V0.1

Data Atlas отображает Evidence Vault через сущности:

- HOT_BUFFER: текущая рабочая россыпь evidence;
- SEALED_PACK: запечатанный пакет;
- PACK_MANIFEST: машинная карта содержимого;
- PACK_INDEX_ENTRY: строка глобального индекса;
- RAW_BUFFER_DELETED: признак, что временная россыпь удалена после seal.

Карточка Data Atlas для pack должна показывать:

- patch_id;
- evidence_pack_id;
- pack size;
- file counts;
- retention class;
- source repo head;
- buffer path;
- raw_buffer_deleted;
- SHA256 пакета.
