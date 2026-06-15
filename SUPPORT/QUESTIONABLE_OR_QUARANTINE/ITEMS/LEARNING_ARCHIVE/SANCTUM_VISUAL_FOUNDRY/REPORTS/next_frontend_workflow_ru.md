# Следующий workflow фронтенда (RU)

Контур после этой задачи: frontend меняется не через «поправить CSS», а через адресный visual topology pipeline.

## Обязательная цепочка

1. Выбрать `visual_address` (например, `SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`).
2. Открыть паспорт unit в `VISUAL_UNITS/*.json`.
3. Проверить owner, states, truth_rules, proof_requirements.
4. Привязать/обновить `visual_tokens` в `TOKENS/token_map_v0_1.json`.
5. Привязать texture и motion только из registry (`TEXTURES/`, `MOTION/`).
6. Сделать изолированную реализацию в `LAB` или целевой UI-слой без выхода за scope.
7. Собрать evidence (скрины/paths/receipts) и обновить mapping report.
8. Прогнать `VALIDATORS/validate_visual_topology.py`.
9. Только после PASS и owner review двигаться к интеграции.

## Жесткие запреты

- Нельзя вводить новый unit без адреса и паспорта.
- Нельзя ставить «green/ready» без source + proof.
- Нельзя переводить stub/locked в real без обновления profile + mapping + receipt.
- Нельзя править вне `IMPERIUM_NEW_GENERATION` в рамках этого контракта.

## Рекомендуемый следующий task

Сделать **один** целевой unit-апгрейд по новой схеме:
`SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL` (улучшение operator cockpit UX с сохранением truth-bind и allowlist-политики).
