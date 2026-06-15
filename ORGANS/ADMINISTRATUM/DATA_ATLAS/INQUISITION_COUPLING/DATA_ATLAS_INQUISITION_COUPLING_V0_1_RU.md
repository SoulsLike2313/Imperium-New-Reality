# Data Atlas / Inquisition Coupling V0.1

Этот слой связывает сущности Data Atlas с выводами Инквизиции.

## Цель

Каждый важный файл должен постепенно получить не только тип и владельца, но и риск-контекст:

- есть ли tool passport;
- есть ли validation recipe;
- не является ли файл runtime leak;
- не является ли файл legacy mirror residue;
- есть ли encoding/mojibake признаки;
- можно ли двигать изменения в main без owner review.

## Отображение в будущей витрине

Data Atlas entity card должна уметь показывать:

- risk count;
- max severity;
- primary risk type;
- recommended next action;
- связанный Mechanicus tool passport;
- связанный Inquisition finding.

## Безопасность

V0.1 только читает и докладывает. Никаких delete/move/cleanup операций.
