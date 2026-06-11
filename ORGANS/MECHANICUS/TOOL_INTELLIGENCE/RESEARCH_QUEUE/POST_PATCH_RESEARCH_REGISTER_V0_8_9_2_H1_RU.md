# Post-Patch Research Register — v0.8.9.2-H1 Backup Hygiene

## Почему research здесь

H1 не добавляет большую фичу. Он закрывает workflow-дефект: локальная backup зона попала в git history. Поэтому research focus — не UI и не storage engine, а hygiene boundary between source and local operator state.

## Внешние ориентиры

1. Git ignore model: `.gitignore` описывает intentionally untracked files, но уже tracked files ignore-правилом не лечатся. Поэтому H1 использует оба слоя: `.gitignore` + `git rm --cached`.
2. Git index cleanup model: `git rm --cached` нужен именно для удаления из index без уничтожения локального файла.
3. Pre-commit style: перед commit должны запускаться быстрые local gates, которые ловят class ошибок до попадания в history.

## Что внести в Imperium doctrine

- Ignore rule не является cleanup. Оно только предотвращает будущий tracking.
- Если мусор уже tracked, нужен explicit index-removal receipt.
- H patch apply scripts должны хранить rollback backups вне repo или создавать ignore protection до backup.
- Future Intelligence Pack Builder должен включать `PASS_PATCH_BACKUP_HYGIENE` как closure proof.

## Что зарегистрировать через Mechanicus

- `inquisition.patch_backup_hygiene_gate`
- будущий `imperium_intelligence_pack_builder` должен зависеть от этого gate.

## Next inspiration queue

- local pre-commit gate bundle для Imperium без обязательной установки внешнего pre-commit framework;
- SQLite-backed patch/session ledger, чтобы patch state не жил только в loose JSON и screenshots;
- graph edges: `patch -> changed_files`, `patch -> evidence`, `patch -> hygiene_gate`, `gate -> doctrine`.
