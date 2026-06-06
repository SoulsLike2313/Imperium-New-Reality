# ДЕКЛАРАЦИЯ ФОРМЫ IMPERIUM NEW GENERATION V0.1 (DRAFT)

> Статус: `DRAFT / NOT FINAL DOCTRINARIUM CANON`  
> Задача: `TASK-20260523-NEWGEN-SERVITOR-PRIME-DECLARATION-OF-FORM-PC-V0_1`  
> Контур: `PC`  
> Область: только `IMPERIUM_NEW_GENERATION/**`

## 1. Opening thesis: что такое `IMPERIUM_NEW_GENERATION`

`IMPERIUM_NEW_GENERATION` сейчас не “готовый продукт”, а операционный полигон, где строится дисциплинированная машина исполнения: через контракты, органные роли, evidence, receipts, state-индексы и ограниченные action-пути.  

Семантически это уже больше, чем “CLI-first skeleton”: внутри есть truth-spine, Sanctum-срезы, transfer-контуры, organ-dialogue foundations и visual contracts. Но это все еще в основном `FOUNDATION_ONLY / PREVIEW_ONLY`, с частичными `PROVED` зонами и заметной долей исторического/runtime шума.

## 2. Agent–IMPERIUM Symbiosis Law

Сервитор не должен работать как изолированный чат. Он должен:

1. опираться на machine-truth (`CURRENT_TRUTH_ROOT`, индексы, contracts);
2. после каждого шага оставлять полезный след в системе (report/receipt/registry/lesson);
3. не маскировать неопределенность;
4. не производить “зеленый” статус без пути к доказательству.

Работа считается полезной только если усиливает сам IMPERIUM, а не только решает локальную задачу.

## 3. Clean Core Target

Цель clean core в NewGen:

1. один правдивый контур управления задачей;
2. scoped verdicts вместо generic PASS;
3. file-backed действия с allowlist и rollback-политикой;
4. органные пакеты как реальные ограничители действий;
5. обязательная граница claim-ов (`FOUNDATION_ONLY`, `NOT_PROVEN`);
6. перенос “памяти боли” в явные preflight-гейты.

## 4. External World / Agent / LLM / Hardware Focusing Model

Смысл модели: внешний хаос (cloud LLM, local LLM, OSS, интернет, PC/VM2/VM3) должен сначала проходить через фокусирующий слой IMPERIUM, а уже потом превращаться в действия.  

Сейчас эта модель уже отображена в `SANCTUM_NG/APP/operator_cockpit_l1.html` как “focus gateway”, но operational-степень пока ограничена read-only и dry-run зонами.

## 5. Internal vs External Modes

Семантически выделяются два режима:

1. `Internal / Vnutryanka`: усиление самого IMPERIUM (truth, gates, контракты, инструменты, continuity).
2. `External / Vneshka`: доставка пользы вовне (клиентские/фриланс задачи, презентации, deliverable bundles).

В текущем дереве сильнее реализован Internal; External пока больше как проектируемый контур.

## 6. Sanctum / Cockpit meaning

`SANCTUM_NG` и `SANCTUM_MINI` вместе означают “экран оператора”, но на разных стадиях:

1. `SANCTUM_MINI`: ранний локальный dashboard с API и allowlisted terminal commands.
2. `SANCTUM_NG`: truth-shell + owner-question gate + servitor-session view + transfer console + action layer.
3. `SANCTUM_NG/OPERATOR_COCKPIT`: попытка собрать Owner L1 cockpit в один экран.

Мой вывод: направление правильное (UI как truth-translator), но до “чистого рабочего ядра” не хватает консолидации и строгой синхронизации живого repo truth с generated state.

## 7. Doctrinarium meaning

Внутри `IMPERIUM_NEW_GENERATION` Doctrinarium пока в основном как skeletal organ и policy-поля в архитектуре/протоколах.  

Смысл Doctrinarium в NewGen: источник непротиворечивого закона исполнения (что разрешено, что блокируется, как формируется PASS/FAIL).  

Текущее ограничение: часть doctrinal law живет не в одном каноническом узле, а распределена между `CORE`, `AUTHORITY_DRAFTS`, `TASK_CONTROL`, внешними `ORGANS/**`.

## 8. Mechanicus meaning

`MECHANICUS` в NewGen — это инженерная машина допусков:

1. `TOOL_ADMISSION` (кандидаты, риски, решения, capability registry);
2. `CONNECTIONS` (SSH/route matrix, bounded proofs);
3. tooling-скрипты/validator’ы в `TOOLS/**`, `TRUTH/**`, `SANCTUM_NG/**`.

Смысл: запрещать “магическую установку/интеграцию” и переводить всё в контракт и доказуемый state.

## 9. Administratum meaning

Administratum — память, инвентаризация, provenance, continuity и маршрутизация артефактов.  

Это наиболее насыщенный орган по фактической реализации (`ORGAN_AGENTS/ADMINISTRATUM_AGENT/**`, множество skills, большой `RUNS` слой, `ARCHIVE`, `LEDGER`, `REPORTS` индексация).

## 10. Officio Agentis meaning

Officio — контроллер роли/режима/формы ответа/ограничений:

1. role registry (`LOGOS_PRIME`, `LOGOS_SPECULUM`, `SERVITOR_PRIME`, `SERVITOR_SPECULUM`);
2. settings registry (permissions, forbidden actions, evidence policy, stop conditions);
3. response contracts (в т.ч. RU owner-facing constraint).

Смысл Officio: не дать агенту “плыть по контексту”, а принудить к контрактному исполнению.

## 11. Inquisition meaning

Inquisition — анти-fake-green и проверка границ scope/evidence.  

В NewGen это частично реализовано как contracts/validators/rules (`NEGATIVE_TESTS`, status semantics, anti-crutch checks), но как автономный живой орган остается на уровне foundation/skeleton.

## 12. Custodes meaning

Custodes в текущей форме — gatekeeper для допуска в зоны и проверок core impact (`FILTER_ZONE_ADMISSION`, `CHECK_ALLOWED_PATHS`, `CHECK_CORE_IMPACT`).  

Смысл: финальный защитник границ. Реализация пока узкая, но семантически критичная.

## 13. Astronomicon meaning

Astronomicon — орган постановки и маршрутизации задачи:

1. нормализация intent в `TASK_FORMATION_*`;
2. stage-map preview;
3. мост к Task Kernel и organ packets.

Смысл: превратить “сырой запрос” в исполнимую, ограниченную форму.

## 14. Strategium meaning

Strategium — орган приоритизации, кампаний и risk-aware sequencing.  

Сейчас mostly skeleton + роль в `TASK_CONTROL` и organ-dialogue contracts.  

Семантика ясна, operational maturity низкая.

## 15. Schola meaning

Schola — контур обучения и извлечения уроков (skill gaps, lesson records, growth loops).  

В репозитории есть contracts/architecture для skill growth, но сильная рабочая “обратная связь в следующую задачу” еще ограничена foundation-уровнем.

## 16. Throne/Core future meaning

`THRONE_AGENT` и `CORE/THRONE_CORE_BOUNDARY.md` задают будущий “верхний контур управления”, но сейчас это намеренно locked/skeleton зона.  

Смысл будущего Throne: концентратор ежедневного операционного контура, а не текущий исполняющий слой.

## 17. Transfer / contour model

Модель контуров уже выделена: `PC`, `VM2`, `VM3`, будущий `THRONE_CORE`.  

Сильная часть: есть bounded route proofs, contracts и ledger’ы в `SANCTUM_NG/TRANSFER_CONSOLE` и `MECHANICUS/CONNECTIONS`.  

Ограничение: это пока не production orchestration; claims корректно ограничены `FOUNDATION_ONLY`.

## 18. Continuity model

Continuity в NewGen понимается как сбор контекста/артефактов для следующей итерации без потери состояния.  

В `SANCTUM_NG/OPERATOR_COCKPIT/DATA/continuity/*` уже есть превью-поток пакетов, но browser-канал частично `PREVIEW_ONLY`, и контур требует дальнейшего уплотнения.

## 19. Pain memory model

Семантически pain memory уже намечена:

1. `NOT_PROVEN_REGISTER`;
2. negative-test catalogs;
3. anti-crutch protocol;
4. status rules с невозможностью “тихого green”.

Но единого “pain-ledger, который автоматически влияет на admission следующей задачи”, пока нет как зрелого ядра.

## 20. Repo hygiene / quarantine model

Сильные стороны:

1. есть explicit scope boundaries;
2. есть runtime/report/receipt separation по смыслу;
3. есть попытки classification и provenance.

Проблема:

1. очень большой объем runtime/report следов внутри git (`RUNS`, `REPORTS`, исторические generated states);
2. часть truth snapshots содержит исторические dirty/head значения;
3. есть риск смешения текущей правды и архивной инерции.

## 21. Development preview / visual contract model

`SANCTUM_VISUAL_FOUNDRY` задает правильный pipeline:

`Owner intake -> visual contract -> tokens -> component manifests -> lab -> screenshots -> validators -> receipts`.

Это сильная семантика. Но в NewGen остается разрыв между visual contracts и “главным рабочим cockpit-контуром”: не все визуальные claims проходят единый жесткий admission gate на уровне всей системы.

## 22. Organ directive / veto model

Целевая модель: орган не “декоративный блок”, а источник разрешений/запретов/проверок.  

Текущее состояние:

1. есть packet contracts, scope merge, dialogue demo;
2. есть response/warning semantics;
3. но живой veto-path в повседневном исполнении пока ограничен foundation-режимом.

## 23. Resource / KPD / cost model

Сильный сигнал в NewGen: обсуждение KPD, bounded scope, stop conditions, no report avalanche, tool admission.  

Но измерение “Owner-visible value per task” еще не закреплено как главный operational metric. Сейчас есть риск локальной оптимизации на количество артефактов, а не на рост полезного operator control.

## 24. Focused local strike method

Метод, который вижу рабочим для NewGen:

1. один узкий operational gap;
2. одна зона изменений;
3. одна проверяемая цепочка evidence;
4. честный scope verdict (`PASS_FOR_X_ONLY / WARN_FOR_Y / BLOCK_FOR_Z`);
5. обязательный write-back в truth/gate/memory слой.

Запрещенный паттерн: “горизонтальное наращивание слоев без интеграции в рабочий контур”.

## 25. PASS criteria (для будущих задач NewGen)

PASS допустим только если одновременно:

1. claim ограничен по области и зрелости;
2. evidence paths существуют и читаемы;
3. неизвестность не скрыта;
4. touched paths не выходят за заявленный scope;
5. есть измеримая прибавка к операционному контролю (а не только новые файлы).

## 26. FAIL criteria

FAIL, если:

1. заявлено больше, чем доказано;
2. verdict не привязан к evidence;
3. нарушение scope или форсирование forbidden paths;
4. повторение taskpack-only workaround вместо канонизации правила;
5. артефакты создают шум без роста управляемости.

## 27. Fake-green criteria

`FAKE_GREEN` фиксируется, когда есть хотя бы один из признаков:

1. `PASS` без твердых ссылок на receipts/validators;
2. UI/visual state зеленый при `UNKNOWN/MISSING/FOUNDATION_ONLY`;
3. “готовность” заявлена при read-only/preview-only факте;
4. production/autonomy claim на базе bounded demo;
5. report говорит “ok”, а current truth root/indices противоречат этому.

## 28. Next focused strengthening strikes

### Strike 1
Синхронизировать `CURRENT_TRUTH_ROOT` с фактическим текущим `HEAD` и реальным деревом NewGen (с маркировкой historical vs current).

### Strike 2
Зафиксировать единый `Operator Cockpit admission gate`: без screenshot/state/evidence/path truth нельзя повышать визуальный или operational verdict.

### Strike 3
Сделать owner-answer write path как bounded file-backed action (с явным audit trail), сохраняя no-autonomy границу.

### Strike 4
Ввести repo hygiene classifier для `CANON/CURRENT_TRUTH/RUNTIME/REPORT/ARCHIVE/QUARANTINE`, чтобы остановить смешение рабочих и исторических артефактов.

### Strike 5
Перевести organ packets из “описательных” в “исполнительные” (required_checks, veto_conditions, allowed_actions, explicit stop rules).

## Что остается неизвестным (честная зона неопределенности)

1. Нет доказательства production-ready orchestration.
2. Нет доказательства live autonomous organ intelligence.
3. Не доказана устойчивая многозадачная эксплуатация Sanctum как единого ежедневного интерфейса.
4. Не завершена канонизация единой doctrinal точки правды для всех NewGen правил.

