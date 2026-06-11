
# Data Atlas / Inquisition Hygiene Coupling V0.1

Data Atlas должен показывать не только файл, но и его hygiene-состояние.

## Новые поля для будущей интеграции

- `hygiene_class`
- `risk_type`
- `ttl_policy`
- `runtime_lifecycle`
- `source_allowed`
- `owner_action_required`
- `cleanup_lane`
- `related_inquisition_finding`
- `related_mechanicus_tool_passport`

## Цель

Открывая entity card, owner должен видеть:

- почему файл лежит в repo;
- является ли он source, fixture, legacy, runtime или грязью;
- есть ли TTL;
- можно ли его удалить/перенести;
- какой орган отвечает за решение.
