# Trinity Patch Contract V0.1

Статус: ACTIVE DRAFT  
Назначение: каждый будущий patch pack должен развивать систему одновременно по трём направлениям.

## Три части патча

### 1. Data Atlas Surface

Патч обязан отвечать на вопрос: **как это видно владельцу и машине?**

Минимальные обязанности:

- добавить или обновить Data Atlas classification;
- показать, где сущность лежит;
- указать owner/organ/storage zone/lifecycle;
- связать entity с Mechanicus passport и Inquisition findings, если применимо;
- не оставлять новые данные невидимыми.

### 2. Inner System / Organ Logic

Патч обязан отвечать на вопрос: **что реально стало умнее или устойчивее внутри?**

Минимальные обязанности:

- новая логика органа или уточнение существующей;
- tool passport или explicit reason why no tool passport is needed;
- validation/smoke/audit route;
- owner-readable report или machine report для важных изменений.

### 3. Architecture / Storage / Process Spine

Патч обязан отвечать на вопрос: **как это хранится, очищается, защищается и масштабируется?**

Минимальные обязанности:

- определить allowed write roots;
- определить retention/TTL;
- запретить raw evidence в source repo;
- связать evidence с Evidence Vault;
- определить cleanup/quarantine/purge gate.

## Patch output rule

Каждый patch run должен стремиться к набору:

- `TRINITY_PATCH_MANIFEST.json`
- `OWNER_SUMMARY_RU.md`
- `MACHINE_REPORT.json`
- evidence buffer during work
- sealed evidence pack after review
- Data Atlas card for new entities
- Inquisition storage findings if dirty writes occur

## Non-goals

Trinity Patch не означает делать огромные изменения без контроля. Это означает, что даже маленький patch не должен быть слепым: он должен быть видимым, внутренне осмысленным и архитектурно размещённым.
