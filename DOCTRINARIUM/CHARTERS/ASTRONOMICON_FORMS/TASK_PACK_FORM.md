# TASK_PACK_FORM (AUTO_PACK)

Форма для задачи, которую будет исполнять Servitor (CODEX / GROK).
Заполняет OWNER_MANUAL или NOTION_OPUS. Структурный вариант — в `TASK_PACK_FORM.template.json`.
Принцип: «всё, что нужно для кристально точного исполнения Servitorом».

## Идентификация

- **task_id**: `<ORGAN>-<TOPIC>-NNNN`
- **title**: одной строкой
- **description**: в прозе — что и зачем (человеческий язык)
- **target_organ(s)**: один или несколько из 9 органов

## Критерии приёмки

- **acceptance_criteria[]**: список проверяемых условий (Astra проверяет их после исполнения)
- **expected_evidence_level**: минимум `E1..E6`

## Scope

- **scope.allow[]**: пути/файлы, которые Servitorу **разрешено** трогать
- **scope.deny[]**: пути/файлы, которые **запрещены**

## Назначение

- **assigned_servitor**: `CODEX | GROK | ANY`
- **deadline**: ISO-8601 или пусто
- **priority**: `LOW | MEDIUM | HIGH | CRITICAL`

## Контекст

- **context_refs[]**: ссылки на документы, прошлые receipts, смежные задачи
- **memory_anchors[]**: якоря в ADMINISTRATUM_MEMORY (опционально)

## После выполнения

Servitor возвращает PATCH_PACK со всеми полями из PATCH_PACK_FORM, и Astra прогоняет его через цикл.
Acceptance_criteria проверяются как часть `WARP_TEST` (или отдельная стадия `ACCEPTANCE_TEST` в v0_2).
