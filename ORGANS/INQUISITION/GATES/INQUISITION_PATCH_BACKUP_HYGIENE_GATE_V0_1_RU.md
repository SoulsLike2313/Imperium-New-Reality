# Inquisition Patch Backup Hygiene Gate v0.1

## Назначение

Gate защищает H/manual patch workflow от попадания локальных operator/workflow зон в source history.

Конкретный инцидент: после `v0.8.9.2` функциональный patch был принят smoke-ом, но `.imperium_patch_backups/` попала в commit через `git add -A`. Это не ломает sealer contract, но делает H branch непригодной для чистого переноса в main без cleanup patch.

## Правило

Локальная backup/handoff/smoke зона не является source.

Запрещённые tracked roots:

- `.imperium_patch_backups/`
- `_LOCAL_HANDOFF/`
- `LOCAL_HANDOFF/`
- `IMPERIUM_EVIDENCE_VAULT_SMOKE*/`
- `EVIDENCE_VAULT_SMOKE*/`
- runtime/test artefacts: `*.trace.zip`, `*.har`, `*.pyc`, `__pycache__`, `.pytest_cache`, `playwright-report`, `test-results`

## Gate states

- `PASS_PATCH_BACKUP_HYGIENE`: forbidden local-only roots не tracked, `.gitignore` содержит managed block.
- `FAIL_PATCH_BACKUP_HYGIENE`: найден forbidden tracked path или отсутствует обязательный ignore pattern.
- `FAIL_NOT_A_GIT_REPO`: указанный root не git repo.

## Ожидаемый H1 transfer result

`git ls-files .imperium_patch_backups` должен быть пустым.

Если ранее backup files уже попали в HEAD, H1 patch должен staged-delete их из git index, оставив локальные файлы на диске. Это означает: backup физически может оставаться у owner-а, но не существует как source.
