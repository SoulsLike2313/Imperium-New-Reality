# ДЕКЛАРАЦИЯ БОЛИ IMPERIUM NEW GENERATION V0.1 (DRAFT)

> Статус: `DRAFT / NOT FINAL DOCTRINARIUM CANON`  
> Task: `TASK-20260523-NEWGEN-SPECULUM-DECLARATION-OF-PAIN-PC-V0_1`  
> Основа формы: `IMPERIUM_NEWGEN_DECLARATION_OF_FORM_OWNER_CORRECTED_RU_V0_2.pdf`  
> Требуемый вердикт этого шага: `PASS_FOR_DECLARATION_OF_PAIN_DRAFT_ONLY`

## 1. Executive verdict

IMPERIUM_NEW_GENERATION не находится в фазе "провалено", но находится в фазе опасного расхождения между **архитектурной дисциплиной** и **операционной полезностью для Owner**.  

Главный диагноз: система уже умеет строить foundation-артефакты, но недостаточно стабильно конвертирует их в один usable cockpit, непрерывность контекста, чистую память боли и управляемое ускорение задач.

Ключевой operational verdict:

`PASS_FOR_DECLARATION_OF_PAIN_DRAFT_ONLY`

Это PASS только на уровень доктринального draft. Это не PASS на production readiness, не PASS на финальный канон, не PASS на завершенность Sanctum/Cockpit.

## 2. Desired Form vs Current Reality

| Desired Form (из Declaration of Form) | Current Reality (live repo) | Разрыв | Последствие |
|---|---|---|---|
| Один открываемый operator cockpit как центр управления | Есть несколько срезов (`SANCTUM_NG`, `OPERATOR_COCKPIT`, `TRANSFER_CONSOLE`), но много `FOUNDATION_ONLY/PREVIEW_ONLY/BLOCKED` | Нет единого устойчивого daily operator loop | Owner продолжает работать через папки и отчеты |
| Current truth должен быть актуален и самосогласован | `README.md`/`NEW_GENERATION_MANIFEST.json` отстают от фактического дерева; `CURRENT_TRUTH_ROOT_V0_1.json` с историческим `head` и `worktree_dirty=true` | Truth split между "историей" и "текущим" | Агентам легко читать устаревшую правду |
| Органы должны реально направлять и блокировать исполнение | Много organ artifacts в режиме `EXAMPLE_ONLY`/`FOUNDATION_DETERMINISTIC_FILE_BACKED_ONLY` | Organ agency не дожата до обязательного veto-path | Органы часто декоративны в боевом потоке |
| Боль должна автоматически становиться gate | Боль фиксируется в отчетах, но не всегда в preflight admission chain | Pain memory не полностью операционализирована | Повторяются одинаковые классы боли |
| Визуал должен быть недефолтным truth-translator | В UI уже есть рост, но сохраняются зоны preview/read-only и риск generic fallback | Visual contract еще не универсальный hard blocker | Повторная визуальная боль и недоверие к green |
| Continuity pack как P0 кнопка и не ручной ритуал | Есть контуры continuity, но не весь путь жестко зафиксирован как mandatory preflight/handoff gate | Непрерывность не гарантирована | Потеря контекста между задачами и чатами |

## 3. Pain Taxonomy

P0-боли (блокируют переход к форме):

1. Owner Power Conversion Failure
2. Default Visual / Weak Cockpit
3. Foundation-Only Fatigue
4. Fake Green / Generic PASS
5. Repo Trash / Artifact Sprawl
6. Continuity Loss
7. Weak Organ Agency
8. Missing Doctrinarium Read Gate
9. Missing Pain Memory
10. Missing Development Preview
11. Resource Burn / KPD Blindness
12. Sovereignty Risk

P1-боли (не блокируют мгновенно, но рушат масштабирование):

13. External/Freelance Readiness Gap
14. Throne/Custodes Future Gap

## 4. Kill / Freeze / Accelerate / Repair

| Решение | Что именно | Причина |
|---|---|---|
| KILL | Generic owner-facing `PASS` без scoped boundary | Производит fake green |
| KILL | Foundation-only задача без owner-visible delta | Увеличивает усталость и не дает cockpit-управления |
| KILL | Декоративная "органность" без veto/checklist | Не дает реальной органной власти |
| KILL | UI claim без screenshots и evidence refs | Повторяет визуальную боль и недоверие |
| FREEZE | Новые широкие roadmap-наращивания до стабилизации cockpit | Растет сложность без роста управляемости |
| FREEZE | Production/autonomy claims | Не доказано текущими артефактами |
| FREEZE | Merge в main/test до recon truth+hygiene | Риск переноса неструктурированной боли в ядро |
| ACCELERATE | Unified operator cockpit (single daily launchpoint) | Прямой канал конверсии в Owner power |
| ACCELERATE | Pain->Gate preflight injection | Прекращает повторяемую боль |
| ACCELERATE | Repo class/quarantine discipline | Останавливает размывание current truth |
| REPAIR | `README`/manifest/truth reconciliation | Убирает конфликт между словами и фактом |
| REPAIR | Organ packets в executable constraints | Переводит органы из темы в управление |

## 5. Pain Classes

### 5.1 Owner Power Conversion Failure
- symptom: много артефактов и отчетов, но Owner не получает стабильный короткий путь "открыл cockpit -> вижу задачу -> управляю действием".
- root cause: метрика прогресса долго была "создан новый слой/реестр/отчет", а не "добавлена owner-visible управляющая способность".
- consequence: архитектурный рост без эквивалентного роста операционной власти Owner.
- damage: демотивация Owner, задержка с переходом к форме "кабина управления силой".
- gate: `GATE-NG-P00-OWNER_POWER_DELTA_REQUIRED`.
- repair task: каждый task обязан начинаться с формулировки owner-visible delta и завершаться доказательством этого delta в cockpit.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/DATA/operator_cockpit_l1_state.generated.json`
  - `IMPERIUM_NEW_GENERATION/README.md`

### 5.2 Default Visual / Weak Cockpit
- symptom: часть UI-срезов остается в preview/foundation, визуальное доверие и скорость считывания правды нестабильны.
- root cause: visual intent не везде принудительно привязан к machine-checkable contract+screenshots+linter.
- consequence: возврат к generic/слабым интерфейсным решениям.
- damage: Owner тратит время на расшифровку состояния вместо управления.
- gate: `GATE-NG-P01-VISUAL_CONTRACT_MANDATORY`.
- repair task: запрет визуальных задач без `visual_contract`, screenshot matrix, anti-default проверок и owner decision note.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/REPORTS/*/screenshot_matrix.json`

### 5.3 Foundation-Only Fatigue
- symptom: критические подсистемы массово помечены как `FOUNDATION_ONLY`.
- root cause: горизонтальное наращивание foundation без жесткого правила "каждый слой сразу в ежедневный operator path".
- consequence: система честная по статусам, но слабая по прикладной управляемости.
- damage: накопление "почти готово" вместо "готово для использования".
- gate: `GATE-NG-P02-FOUNDATION_ONLY_BUDGET`.
- repair task: ввести лимит foundation-only задач подряд; после 2 задач обязательна конверсия в owner-usable panel/action.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json`

### 5.4 Fake Green / Generic PASS
- symptom: риск трактовать технический PASS как продуктовую готовность.
- root cause: недостаточный разрыв между "schema/validator pass" и "owner-usable pass".
- consequence: ложное завершение задач, которые не закрыли боль.
- damage: потеря доверия к вердиктам и отчетам.
- gate: `GATE-NG-P03-NO_GENERIC_PASS`.
- repair task: owner-facing вердикт только scoped (`PASS_FOR_<X>_ONLY`) + обязательные `NOT_PROVEN` и `NOT_RUN`.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/REPORTS/*/FINAL_REPORT.md`
  - `IMPERIUM_NEW_GENERATION/TRUTH/NOT_PROVEN_REGISTER_V0_1.json`

### 5.5 Repo Trash / Artifact Sprawl
- symptom: высокая концентрация runtime/report файлов (`RUNS`, `REPORTS`) и рост когнитивного шума.
- root cause: слабая принудительная классификация `CANON/CURRENT_TRUTH/REPORT/RUNTIME/ARCHIVE/QUARANTINE`.
- consequence: current truth смешивается с историческими и тяжелыми артефактами.
- damage: снижение скорости разведки репо и рост риска ошибочных выводов.
- gate: `GATE-NG-P04-REPO_CLASSIFICATION_REQUIRED`.
- repair task: обязательный classifier для новых артефактов и quarantine route для тяжелых/временных outputs.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/RUNS/**`
  - `IMPERIUM_NEW_GENERATION/REPORTS/**`

### 5.6 Continuity Loss
- symptom: handoff между задачами и чатами не всегда гарантирован единым жестким каналом.
- root cause: continuity иногда остается "полезной опцией", а не admission требованием.
- consequence: повторный сбор контекста и потеря решения/ограничений.
- damage: ресурсный burn, замедление исполнения, повтор боли.
- gate: `GATE-NG-P05-CONTINUITY_PACK_MANDATORY`.
- repair task: обязательный continuity pack small/normal/full для задач выше P1-риска и для контурного handoff.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/DATA/continuity/**`
  - `IMPERIUM_NEW_GENERATION/TRUTH/README_CURRENT_TRUTH_ROOT_V0_1.md`

### 5.7 Weak Organ Agency
- symptom: у органных пакетов и dialogue есть foundation, но live influence ограничен.
- root cause: органные ответы не всегда обязательны как execution blockers/veto.
- consequence: органы остаются advisory, а не управляющей силой.
- damage: исполнение может обходить organ intelligence.
- gate: `GATE-NG-P06-ORGAN_VETO_ENFORCEMENT`.
- repair task: hard-binding `required_checks/forbidden_actions/stop_conditions` в pre-execution policy.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/ORGAN_PACKET_V0_1.schema.json`
  - `IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/REGISTRY/ORGAN_DIALOGUE_CAPABILITY_MATRIX_V0_1.json`

### 5.8 Missing Doctrinarium Read Gate
- symptom: часть задач может стартовать из локального контекста агента без жесткого doctrinarium read-first chain.
- root cause: отсутствует единый обязательный preflight чек с доказательством чтения Form+Pain.
- consequence: drift интерпретаций и повторение старых ошибок.
- damage: ослабление доктринальной целостности.
- gate: `GATE-NG-P07-DOCTRINARIUM_READ_FIRST`.
- repair task: для каждой задачи обязательный ACK: Form read, Pain read, active gates list, allowed/forbidden path verdict.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DECLARATIONS/DECLARATION_OF_FORM/IMPERIUM_NEWGEN_DECLARATION_OF_FORM_OWNER_CORRECTED_RU_V0_2.pdf`
  - `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DECLARATIONS/DECLARATION_OF_PAIN/**`

### 5.9 Missing Pain Memory
- symptom: pain classes фиксируются в отчетах, но не всегда переходят в автоматический блокер следующей задачи.
- root cause: отсутствует единый pain registry с preflight injection.
- consequence: повторяемость боли "каждый раз заново".
- damage: низкая обучаемость системы между задачами.
- gate: `GATE-NG-P08-PAIN_PREFLIGHT_REQUIRED`.
- repair task: ввести machine-readable pain ledger и связывать его с task admission.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/TRUTH/NOT_PROVEN_REGISTER_V0_1.json`
  - `IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/**`

### 5.10 Missing Development Preview
- symptom: часть development preview flow не является обязательной доказательной цепочкой перед приемкой визуальных/операторских изменений.
- root cause: preview и screenshot discipline местами остается soft-обязательством.
- consequence: позднее обнаружение визуальных и UX-ошибок.
- damage: переработки и недоверие к визуальному прогрессу.
- gate: `GATE-NG-P09-DEV_PREVIEW_SCREENSHOT_REQUIRED`.
- repair task: обязательные preview states + screenshot matrix + changed files summary + owner stop/note.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/operator_cockpit_l1.html`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/REPORTS/*/screenshot_matrix.json`

### 5.11 Resource Burn / KPD Blindness
- symptom: высокий объем артефактов и шагов не всегда сопоставлен с owner-visible delta.
- root cause: KPD часто фиксируется после факта, а не как допуск до запуска.
- consequence: задачи с высоким затратным профилем и низкой полезной плотностью.
- damage: сгорание Owner и снижение темпа.
- gate: `GATE-NG-P10-KPD_BUDGET_REQUIRED`.
- repair task: pre-task KPD budget: expected delta, budgeted commands/artifacts, stop threshold.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/**/agent_kpd_self_review.json`
  - `IMPERIUM_NEW_GENERATION/RUNS/**`

### 5.12 Sovereignty Risk
- symptom: часть контуров/инструментов остается в статусе bounded/demo, а внешняя зависимость может блокировать операцию.
- root cause: суверенные fallback-пути не всегда закреплены как обязательный слой.
- consequence: деградация управляемости при отказе внешних инструментов/маршрутов.
- damage: операционная нестабильность и потеря скорости.
- gate: `GATE-NG-P11-SOVEREIGN_FALLBACK_REQUIRED`.
- repair task: для каждого критичного действия иметь local deterministic fallback и clearly declared non-availability state.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/CONNECTIONS/**`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/contours/**`

### 5.13 External/Freelance Readiness Gap
- symptom: контур внешней поставки еще слабее внутреннего, package discipline не везде operationalized.
- root cause: фокус на internal foundation без полного delivery pipeline.
- consequence: риск сорвать внешнюю задачу по качеству handoff.
- damage: коммерческий и репутационный риск.
- gate: `GATE-NG-P12-DELIVERABLE_PACKAGE_REQUIRED`.
- repair task: обязательные package manifest + QA checklist + presentation + scoped limitations для внешних задач.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/REPORTS/**`
  - `IMPERIUM_NEW_GENERATION/TASK_CONTROL/**`

### 5.14 Throne/Custodes Future Gap
- symptom: будущий Throne/Core и Custodes расширение пока не имеют достаточной operational синхронизации с текущими pain gates.
- root cause: будущий верхний контур описан, но не прошит текущими admission hooks.
- consequence: риск повторения старых болей при переходе в следующий уровень.
- damage: перенос незакрытых долгов в будущий управляющий слой.
- gate: `GATE-NG-P13-THRONE_TRANSITION_BOUNDARY`.
- repair task: определить transition criteria: что должно быть доказано до эскалации в Throne/Core.
- evidence required:
  - `IMPERIUM_NEW_GENERATION/CORE/**`
  - `IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json`

## 6. Blocked Patterns

Немедленно блокировать:

1. `PASS` без scoped boundary и без `NOT_PROVEN`.
2. Визуальные задачи без visual contract и screenshot matrix.
3. Задачи, которые пишут новые foundation артефакты без owner-visible integration.
4. Action button без request/result receipts.
5. Изменения вне declared scope.
6. Ручной "поиск правды" Owner через десятки папок вместо cockpit-среза.
7. Старт задачи без доказанного чтения Form+Pain.
8. Коммиты runtime-heavy артефактов без класса и quarantine решения.

## 7. Required Gates

Добавить/активировать как обязательные pain-gates:

1. `GATE-NG-P00-OWNER_POWER_DELTA_REQUIRED`
2. `GATE-NG-P01-VISUAL_CONTRACT_MANDATORY`
3. `GATE-NG-P02-FOUNDATION_ONLY_BUDGET`
4. `GATE-NG-P03-NO_GENERIC_PASS`
5. `GATE-NG-P04-REPO_CLASSIFICATION_REQUIRED`
6. `GATE-NG-P05-CONTINUITY_PACK_MANDATORY`
7. `GATE-NG-P06-ORGAN_VETO_ENFORCEMENT`
8. `GATE-NG-P07-DOCTRINARIUM_READ_FIRST`
9. `GATE-NG-P08-PAIN_PREFLIGHT_REQUIRED`
10. `GATE-NG-P09-DEV_PREVIEW_SCREENSHOT_REQUIRED`
11. `GATE-NG-P10-KPD_BUDGET_REQUIRED`
12. `GATE-NG-P11-SOVEREIGN_FALLBACK_REQUIRED`
13. `GATE-NG-P12-DELIVERABLE_PACKAGE_REQUIRED`
14. `GATE-NG-P13-THRONE_TRANSITION_BOUNDARY`

## 8. Next 3 Tasks

1. `TASK-20260524-NEWGEN-PAIN-GATE-REGISTRY-INTEGRATION-PC-V0_1`  
   Цель: формально зарегистрировать pain-gates как machine-readable admission слой.
2. `TASK-20260524-NEWGEN-CURRENT-TRUTH-RECONCILIATION-PC-V0_1`  
   Цель: согласовать `README`/manifest/current truth с фактическим состоянием NewGen.
3. `TASK-20260524-NEWGEN-DOCTRINARIUM-READ-FIRST-ENFORCEMENT-PC-V0_1`  
   Цель: без Form+Pain ACK задача не может стартовать.

## 9. Next 7 Tasks

1. `TASK-20260524-NEWGEN-PAIN-GATE-REGISTRY-INTEGRATION-PC-V0_1`
2. `TASK-20260524-NEWGEN-CURRENT-TRUTH-RECONCILIATION-PC-V0_1`
3. `TASK-20260524-NEWGEN-DOCTRINARIUM-READ-FIRST-ENFORCEMENT-PC-V0_1`
4. `TASK-20260524-NEWGEN-REPO-CLASSIFIER-QUARANTINE-ENFORCEMENT-PC-V0_1`
5. `TASK-20260524-NEWGEN-CONTINUITY-PACK-MANDATORY-HANDOFF-PC-V0_1`
6. `TASK-20260524-NEWGEN-ORGAN-VETO-RUNTIME-BINDING-PC-V0_1`
7. `TASK-20260524-NEWGEN-KPD-BUDGET-PREFLIGHT-PC-V0_1`

## 10. Next 14 Tasks

1. `TASK-20260524-NEWGEN-PAIN-GATE-REGISTRY-INTEGRATION-PC-V0_1`
2. `TASK-20260524-NEWGEN-CURRENT-TRUTH-RECONCILIATION-PC-V0_1`
3. `TASK-20260524-NEWGEN-DOCTRINARIUM-READ-FIRST-ENFORCEMENT-PC-V0_1`
4. `TASK-20260524-NEWGEN-REPO-CLASSIFIER-QUARANTINE-ENFORCEMENT-PC-V0_1`
5. `TASK-20260524-NEWGEN-CONTINUITY-PACK-MANDATORY-HANDOFF-PC-V0_1`
6. `TASK-20260524-NEWGEN-ORGAN-VETO-RUNTIME-BINDING-PC-V0_1`
7. `TASK-20260524-NEWGEN-KPD-BUDGET-PREFLIGHT-PC-V0_1`
8. `TASK-20260525-NEWGEN-DEV-PREVIEW-SCREENSHOT-GATE-PC-V0_1`
9. `TASK-20260525-NEWGEN-VISUAL-CONTRACT-HARD-BLOCK-PC-V0_1`
10. `TASK-20260525-NEWGEN-OWNER-ANSWER-WRITE-PATH-HARDENING-PC-V0_1`
11. `TASK-20260525-NEWGEN-PAIN-MEMORY-LEDGER-INJECTION-PC-V0_1`
12. `TASK-20260525-NEWGEN-EXTERNAL-DELIVERABLE-PACKAGE-POLICY-PC-V0_1`
13. `TASK-20260526-NEWGEN-SOVEREIGN-FALLBACK-MATRIX-PC-V0_1`
14. `TASK-20260526-NEWGEN-THRONE-TRANSITION-CRITERIA-PC-V0_1`

## 11. What must be refused until fixed

Отказывать:

1. Любой задаче, которая просит "финальный green" при `FOUNDATION_ONLY/PREVIEW_ONLY`.
2. Любому merge-сценарию в main/test без pain-gate integration и repo-classification.
3. Любому визуальному релизу без screenshot evidence и visual contract.
4. Любым задачам с broad scope без owner-visible delta.
5. Любым "autonomy/production-ready" claims без повторяемых proof loops.

## 12. How future tasks read Form + Pain through Doctrinarium

Обязательная цепочка запуска будущей задачи:

1. Read `Declaration of Form` из Doctrinarium.
2. Read `Declaration of Pain` (active draft/canon) из Doctrinarium.
3. Сформировать `GATE_ACK` с перечислением применимых universal и pain-gates.
4. Объявить allowed/forbidden paths и expected receipts до правок.
5. Определить pain class impact: какую боль задача уменьшает и как это доказывается.
6. Выполнить bounded work.
7. Закрыть scoped verdict (`PASS_FOR_<X>_ONLY`/`WARN_FOR_<Y>`/`BLOCK_FOR_<Z>`).
8. Обновить pain memory/registry при обнаружении новой повторяемой боли.

## 13. Open questions / uncertainty

1. Какая точная политика хранения для тяжелых runtime outputs должна стать canonical (git vs local private) для всех контуров?
2. Какой минимальный набор owner-actions должен стать `WIRED`, чтобы считать cockpit реально usable daily surface?
3. Какая формальная граница между "foundation growth допустим" и "foundation fatigue блокируется" (например, по количеству задач подряд)?
4. Когда именно переходить от deterministic organ dialogue к bounded semi-live logic без overclaim?

## 14. Draft boundary statement

Этот документ является черновой доктриной боли и не претендует на статус финального канона Doctrinarium.  
Его функция: зафиксировать проверяемые pain classes, блокирующие паттерны и gate-переход от боли к управляемым задачам.
