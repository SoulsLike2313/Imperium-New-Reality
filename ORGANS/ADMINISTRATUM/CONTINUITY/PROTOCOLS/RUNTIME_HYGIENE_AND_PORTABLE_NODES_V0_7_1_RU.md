# Runtime Hygiene and Portable Nodes v0.8

Цель: остановить расползание временных форм, скринов, отчётов и WARP-копий по диску.

Канонические имена:

- MAIN_REPO — чистый pushed source repository.
- H_CONTOUR — ручной owner-review контур.
- WARP_ROOT — временные рабочие контуры.
- LOCAL_HANDOFF — runtime/evidence/forms/reports вне source.
- TASK_FORMS — скачанные Astronomicon формы задач.
- WARP_RUNS — stage ledger, jobs, receipts.
- SERVITOR_OUTPUTS — Servitor outputs and patch bundles.
- REPORT_BUNDLES — финальные owner-visible bundles.
- RESOURCE_FLEET — диагностика машин, которые могут стать узлами Империума.

Правило TTL:

- временные runtime/evidence/task forms живут 3 дня по умолчанию;
- `_registry`, active WARP и active WARP_RUN защищены;
- web action выполняет только scan;
- фактическое удаление доступно только CLI командой `prune --apply`.

Принцип portable node:

- новый ноут/сервер/Ubuntu-узел сначала запускает node probe;
- probe фиксирует OS, Python, git, node/npm, repo/root aliases;
- узел добавляет вычислительную силу, но не получает authority: органы, taskpack и gates остаются источником права на работу.
