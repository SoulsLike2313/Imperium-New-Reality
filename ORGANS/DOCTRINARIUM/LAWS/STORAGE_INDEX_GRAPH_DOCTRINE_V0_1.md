# Storage / Index / Graph Doctrine V0.1

Patch: `v0.8.9.2`
Owner directive: не плодить тупые repo snapshots; строить лёгкое, быстро читаемое, индексируемое хранение.

## Doctrine

1. **Source repo is not a dump.** Source хранит код, схемы, маленькие fixtures с manifest, policies и doctrine. Evidence/raw runtime живёт вне source.
2. **Packs are transport; indexes are memory.** ZIP может быть каноническим пакетом evidence, но рабочая память системы должна читать manifest/index/SQLite/graph edges без распаковки.
3. **SQLite-first for local machine truth.** Когда JSON snapshots становятся тяжёлыми, следующий слой — локальный SQLite индекс: files, tools, organs, evidence packs, findings, passports, relations.
4. **Graph edges over prose-only summaries.** Каждый patch должен по возможности порождать edges вида `file -> organ`, `tool -> passport`, `finding -> risk`, `evidence_pack -> patch`, `patch -> doctrine`.
5. **Owner-visible card over raw wall of JSON.** Data Atlas показывает карточку состояния; raw JSON остаётся в machine details.
6. **Post-patch research is part of closure.** После каждого patch-pack создаётся research/register pass: что регистрировать в Mechanicus, что добавить в doctrine, какие внешние архитектуры взять как ориентир.
7. **Internal agents must improve.** Патч считается сильнее, если после него Mechanicus/Inquisition/Data Atlas/Administratum лучше выбирают tools, читают evidence и объясняют риски.

## Immediate architecture direction

- `IMPERIUM_INTELLIGENCE_PACK` вместо crude full repo dump.
- `Atlas SQLite Index Builder` как следующий storage spine.
- `Graph Edge Exporter` для связей между органами, файлами, findings, evidence и doctrine.
- `Sealed Pack Health Card` как первый owner-visible proof card.
