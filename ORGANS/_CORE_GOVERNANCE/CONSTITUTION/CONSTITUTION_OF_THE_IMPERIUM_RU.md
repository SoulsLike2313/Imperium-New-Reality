# Конституция Империума

Статус: `CANON_ACTIVE`
Область: `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY`
Owner canonization approval: `true`
Canonization task: `TASK-NEWREALITY-GOVERNANCE-CANON-MECHANICUS-ULTRA-IDE-FOUNDATION-PC-V0_1`
Canonization timestamp UTC: `2026-06-07T11:08:13Z`

## 1. Иерархия власти

1. Паспорт Императора.
2. Конституция Империума.
3. Корневой контракт `AGENTS.md`.
4. Контракты органов и read-first files.
5. Taskpacks Astronomicon.
6. Tool cards и validators.
7. Reports и receipts.

## 2. Базовые органы

Базовые органы: Astronomicon, Administratum, Architectum, Strategium, Mechanicus, Doctrinarium, Inquisition, Custodes и Officio. `_CORE_GOVERNANCE` и `_POST_WORK_RING` являются вспомогательными control zones. SPECULUM остается кандидатом до допуска владельцем.

## 3. Закон жизненного цикла задачи

Каждой задаче нужен registered taskpack или эквивалентная инструкция владельца, явный scope, admission result, execution receipts, validation receipts и closure evidence. BLOCK требует доказательства; PASS требует валидации и git truth.

## 4. Уровни доказательств

Receipt сильнее памяти. Live command output сильнее старых отчетов. Git status и commit/push state обязательны для финального закрытия write-задач, если manifest это разрешает.

## 5. Обязанности Astronomicon

Astronomicon отвечает за task intake, task registry truth, route manifest templates, start acknowledgements и route discovery. PC-local задачи не должны требовать remote contours, если manifest не требует обратного.

## 6. Обязанности Mechanicus

Mechanicus отвечает за reusable tools и tool evidence. Инструмент считается reusable только при наличии tool card, registry seed entry или явного candidate status с dependencies, command interface, risk class и last validation receipt.

## 7. Обязанности Inquisition

Inquisition отвечает за contradiction checks, fake-green scans, scope violations, secret exposure checks и claims audit. Частичная или inferred truth должна называться частичной или inferred.

## 8. Обязанности Administratum

Administratum отвечает за records, indexes, report placement, continuity packs и ownership metadata. Owner-facing records должны быть краткими, technical records - воспроизводимыми.

## 9. Закон cleanup и quarantine

Cleanup начинается с классификации и staging, а не удаления. Unknown zones блокируют автоматизацию. Moves требуют allowlist, denylist, batch plan, rollback evidence и owner approval, если batch затрагивает legacy, quarantine, reports или active organ files.

## 10. Закон validated push и remote closure

Commit и push обязательны для non-BLOCK completed write-задач, если они не запрещены manifest или не заблокированы доказательством. Push разрешен только после проверки scope, secret safety, отсутствия forbidden actions и обязательных артефактов.

## 11. Закон языка

Owner-facing коммуникация следует требованиям Officio. Technical artifacts могут оставаться English-safe, если это улучшает machine readability или validation.

## 12. Закон безопасности

Local route configs, secrets, credentials и machine-local tokens нельзя staging/push. Local operator configs можно читать для current receipts только когда scope задачи это разрешает.

## 13. Закон продуктовой ориентации

Architecture, governance и tooling должны служить owner-visible outcomes. Новая структура должна уменьшать риск, повышать repeatability, прояснять authority или помогать delivery продукта.
