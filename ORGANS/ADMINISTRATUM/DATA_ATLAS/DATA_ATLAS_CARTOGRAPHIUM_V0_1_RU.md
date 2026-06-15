# Data Atlas / Cartographium v0.1

Цель: дать owner-visible read-only слой видимости данных внутри Web Sanctum.

## Что показывает

- где лежат файлы и директории;
- к какому органу относится сущность;
- какой у неё тип: script, protocol, registry, report, evidence, runtime residue, archive, UI surface;
- есть ли паспорт или нужен паспорт;
- есть ли dirty/untracked/source-runtime leak/large/archive/duplicate flags;
- какие органы перегружены, где грязь и где недостаёт паспортов.

## Правило безопасности

Data Atlas v0.1 ничего не удаляет, не переносит и не делает произвольный shell. Web action `data_atlas_scan` read-only. Интерактивная очистка разрешается только будущим отдельным этапом после owner review.

## Визуальный принцип

JSON остаётся в trace/details, но основной экран показывает карточки, карту органов, фильтруемый explorer и человеческий паспорт сущности на русском/английском.
