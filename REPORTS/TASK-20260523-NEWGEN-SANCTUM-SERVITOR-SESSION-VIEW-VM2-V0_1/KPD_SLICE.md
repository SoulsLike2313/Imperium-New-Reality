# KPD_SLICE

## Что было лишним
- Повторные чтения длинных STEP_PROOF в старых задачах, где хватало структурированного summary.

## Чего не хватало
- Единый стандартный parser для разноформатных STEP_PROOF_RECORDS.jsonl (timestamp/status fields).

## Какие инструменты стоит сохранить
- build_servitor_session_view_v0_1.py
- validate_servitor_session_view_v0_1.py

## Узкий профиль следующего агента
- Узкоспециализированный `Session-View Harmonizer` для нормализации run/rerun timeline и source-report статусов.

## Как повысить action-density
- Держать реестр latest report categories в отдельном machine-readable index, чтобы не сканировать REPORTS по токенам.
