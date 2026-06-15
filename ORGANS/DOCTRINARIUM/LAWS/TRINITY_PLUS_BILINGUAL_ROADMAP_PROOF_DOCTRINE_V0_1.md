# Trinity Plus Bilingual Roadmap Proof Doctrine v0.1

## Назначение

Trinity Plus patch должен не только менять систему, но и показывать владельцу живую смотровую. Начиная с этого закона, смотровая должна быть понятна на русском и английском, а также показывать движение по плану: что уже видно, что работает, какие lanes открыты, насколько близко состояние к общей цели.

## Trinity remains three-part

Trinity patch всё ещё состоит из трёх архитектурных частей:

1. Data Atlas visibility.
2. Inner System / Organ Logic.
3. Architecture / Storage / Process Spine.

`Plus` не заменяет эти части. `Plus` добавляет исполнительную proof-surface: owner-visible terminal/web/markdown/dashboard proof.

## Roadmap proof law

Every Trinity Plus proof SHOULD expose:

- what changed;
- what works;
- source head and patch id;
- lane counts and top review zones;
- owner gate / no automatic cleanup warning;
- roadmap progress to the current strategic goal;
- RU and EN owner-readable text;
- machine JSON for future Data Atlas / Warp dashboards.

## Progress honesty

Progress bars are operator indicators, not legal cleanup authorization. A percent can show visibility, classification, or estimated closure status, but it must not imply that source deletion is authorized.

## Rich terminal direction

Visual proof tools MAY use Rich if available, but MUST keep a plain fallback. External visual dependencies must not become required for smoke unless explicitly registered through Mechanicus and accepted by owner gate.
