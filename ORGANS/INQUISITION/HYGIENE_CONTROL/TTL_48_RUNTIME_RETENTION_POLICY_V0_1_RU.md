
# TTL-48 Runtime Retention Policy V0.1

Назначение: отделить исходную правду репозитория от временных evidence/runtime/screenshot/debug артефактов.

## Канон

- Source repo не является складом runtime-output.
- Скриншоты, Playwright evidence, debug packs, временные bundles и operator handoff outputs живут вне source repo.
- Стандартный срок жизни временных runtime/evidence артефактов: **48 часов**.
- Очистка source repo не выполняется автоматически, кроме очевидных generated cache файлов при отдельном owner-approved режиме.
- Локальные TTL-кандидаты сначала получают classification report и cleanup plan.

## Safe cleanup lanes

1. `DRY_RUN` — только отчёт, без изменений.
2. `QUARANTINE` — перенос локальных TTL-кандидатов в `_LOCAL_HANDOFF/QUARANTINE`, без удаления.
3. `DELETE_QUARANTINE` — удаление только уже помещённой quarantine-грязи, отдельным будущим gate.

## Source repo rule

В source repo Inquisition только классифицирует:

- runtime/cache leaks;
- archive review candidates;
- screenshots/logs/temp files;
- unregistered folders;
- tool-like scripts without passports;
- encoding/mojibake traces;
- write actions without declared safety.

Удаление/перенос source-файлов допускается только отдельным owner-reviewed patch после Data Atlas/Mechanicus/Inquisition отчёта.
