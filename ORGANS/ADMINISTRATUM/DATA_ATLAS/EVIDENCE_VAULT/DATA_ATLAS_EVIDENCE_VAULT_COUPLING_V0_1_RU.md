# Data Atlas / Evidence Vault Coupling V0.1

Data Atlas обязан показывать evidence не как россыпь файлов, а как сущности:

- HOT_BUFFER — активный буфер текущего patch-run;
- SEALED_PACK — запечатанный evidence pack;
- PINNED_EVIDENCE — доказательство, которое нельзя удалять по TTL;
- TTL_48 — временная evidence зона;
- QUARANTINE — убрано из активной зоны, но ещё не уничтожено;
- PURGE_ALLOWED — разрешено к удалению отдельным gate.

## Card fields

Evidence Pack card должна показывать:

- patch id;
- created_at_utc;
- source head;
- size;
- counts by content type;
- retention class;
- raw buffer deleted: yes/no;
- linked Inquisition findings;
- linked Mechanicus tools;
- owner summary path;
- manifest path.

## Правило

Data Atlas не должен индексировать каждую временную картинку как вечную сущность, если она уже запечатана в pack. Он должен показывать pack и manifest, а raw-buffer считать временным состоянием.
