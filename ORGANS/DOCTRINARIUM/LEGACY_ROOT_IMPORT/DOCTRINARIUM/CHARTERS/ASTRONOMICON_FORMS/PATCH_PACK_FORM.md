# PATCH_PACK_FORM (HAND_PACK)

Форма для ручного патч-пака. Заполняет OWNER_MANUAL или NOTION_OPUS.
Структурированный вариант — в `PATCH_PACK_FORM.template.json`.
Принцип: «всё, что нужно для кристально точного исполнения».

## Идентификация

- **task_id**: `ASTRON-<TOPIC>-NNNN` (или `<ORGAN_CODE>-<TOPIC>-NNNN` для других органов)
- **title**: одной строкой по-русски, суть изменения
- **target_organ**: один из `ADMINISTRATUM | ASTRONOMICON | CUSTODES | DOCTRINARIUM | INQUISITION | MECHANICUS | OFFICIO_AGENTIS | SCHOLA_IMPERIALIS | STRATEGIUM`
- **change_kind**: `PATCH | NEW_FILE | DELETE | REFACTOR | DOC`
- **intent**: зачем это меняем, 1-3 предложения

## Payload

- **payload[]**: список путей файлов внутри пака (`files/<...>`)
- **integration.mode**: `copy` (сейчас единственный режим)
- **integration.map**: `{ "files/x": "<target path в repo>", ... }`

## Evidence (доказательства)

- **declared_evidence_level**: один из `E1..E6`
  - `E1`: документы/markdown, нет исполняемого
  - `E2`: код, но без прогона (PowerShell, TUI, curses)
  - `E3`: код + прогон в sandbox (Python e2e)
  - `E4-E6`: прогоны в контуре / множественные / производственные стенды
- **execution_log**: `EXECUTION_LOG.txt` (обязателен для E3+)
- **verify.cmd**: `["python3", "-c", "..."]` — как Astra проверит пак в варп-тесте
- **verify.cwd**: опциональный относительный путь

## Авторство и контур

- **submitted_by**: `OWNER_MANUAL | SERVITOR` (для ручных паков: `OWNER_MANUAL`)
- **author**: `NOTION_OPUS | CODEX | GROK | OWNER_MANUAL`
- **form**: `CHAT | CLI`
- **model**: опционально (для LLM: `Opus 4.8` и т.д.)
- **contour**: `WINDOWS_PC | SANDBOX | ...`

## План отката (rollback)

- **rollback_plan**: как вернуть master назад при проблемах (`git revert <land_sha>`, список ручных шагов).

## Итог
TASK_MANIFEST.json в паке формируется из этой формы автоматически (Astra в HAND_PACK).
PROVENANCE в HAND_PACK подписывается Astra от имени `author`/`form`/`model`, указанных в форме.
