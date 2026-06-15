# Doctrine: WARP Diff Room v0.1 (observational viewing room)

**Authority refs:** Constitution §6 (reusable tools), §13 (UX product), Passport §3 (sovereign observation), Passport §5 (no fake green).

## Цель

Комната просмотра диффов: **наблюдательный** HTML-артефакт, показывающий что изменилось от прошлого коммита (`HEAD~1..HEAD` по умолчанию). Один файл, открывается в браузере без сервера.

## Границы (что НЕЛЬЗЯ)

- НЕ коммитить, НЕ пушить, НЕ менять историю git.
- НЕ писать внутрь source-репо. Артефакт живёт в `_LOCAL_HANDOFF/WARP_DIFF_ROOM/`.
- НИКАКИХ действий на данные: только чтение (`git rev-parse`, `git log -1`, `git diff`).
- НЕ вносить в комнату сверх-функциональность (без cherry-pick, без стейджа, без принятия решений). Наблюдение и всё.

## Форма

Единая форма Web Sanctum: `diff_room_shell.css` зеркалит токены `ORGANS/IMPERIAL_IDE/WEB_SANCTUM/app/styles.css` (палитра --gold/--ember/--violet, фоны Inter+Georgia, сетка `.shell` 260px+1fr, `.relic-frame`/`.panel`/`.card`, `pre`). Комната будет встраиваться в санктум как пункт меню зоны варпа.

## Механика

Генератор `warp_diff_room_v0_1.py`:
1. `git -C repo rev-parse/log/diff` — только чтение.
2. Парсит `--name-status` и разбивает `git diff` на пофайловые блоки.
3. Рендерит self-contained HTML: топбар (branch / base→head / rev), карты (files / +ins / -del), факты коммита, сайдбар по файлам, панели с крашенными ханками.
4. Пишет `WARP_DIFF_ROOM.html` + `WARP_DIFF_ROOM.summary.json` в `_LOCAL_HANDOFF/WARP_DIFF_ROOM/`.

## Будущее (не в v0.1)

- Встроить комнату внутрь Web Sanctum как вкладку "🌀 WARP · Diff Room".
- Разрешить выбор range (`HEAD~N..HEAD`, диапазон коммитов).
- Индекс side-by-side, фильтр по органам, hot-reload.
