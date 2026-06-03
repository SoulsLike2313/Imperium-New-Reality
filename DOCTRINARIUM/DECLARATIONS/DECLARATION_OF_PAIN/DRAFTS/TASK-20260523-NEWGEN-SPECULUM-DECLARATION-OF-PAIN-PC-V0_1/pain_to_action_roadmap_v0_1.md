# Pain -> Action Roadmap V0.1 (Draft)

Task: `TASK-20260523-NEWGEN-SPECULUM-DECLARATION-OF-PAIN-PC-V0_1`  
Status: `DRAFT / NOT FINAL CANON`  
Verdict target: `PASS_FOR_DECLARATION_OF_PAIN_DRAFT_ONLY`

## 1. Цель roadmap

Прекратить режим "боль описана, но не операционализирована".  
Каждая боль должна перейти в:

1. gate;
2. ремонтный task;
3. measurable acceptance signal;
4. правило блокировки будущих задач.

## 2. Принцип исполнения

1. Один task = один измеримый owner-visible delta.
2. Нет generic PASS.
3. Нет task-start без Form+Pain admission.
4. Если боль повторилась, но gate не обновлен: задача считается неполной.

## 3. Pain-to-Action Table

| Pain class | Gate | Action priority | Repair task focus | Acceptance signal |
|---|---|---|---|---|
| Owner Power Conversion Failure | `GATE-NG-P00-OWNER_POWER_DELTA_REQUIRED` | P0 | Каждая задача доказывает owner-visible control delta | В cockpit видно новое действие/управление, а не только новый отчет |
| Default Visual / Weak Cockpit | `GATE-NG-P01-VISUAL_CONTRACT_MANDATORY` | P0 | Visual contract + screenshots + anti-default linter | Visual task без contract/screenshot не проходит |
| Foundation-Only Fatigue | `GATE-NG-P02-FOUNDATION_ONLY_BUDGET` | P0 | Лимит foundation-only задач подряд | После лимита обязателен usable slice |
| Fake Green / Generic PASS | `GATE-NG-P03-NO_GENERIC_PASS` | P0 | Scoped verdict + NOT_PROVEN/NOT_RUN | Нет owner-facing `PASS` без области |
| Repo Trash / Artifact Sprawl | `GATE-NG-P04-REPO_CLASSIFICATION_REQUIRED` | P0 | Artifact classifier + quarantine | Новый heavy output классифицирован |
| Continuity Loss | `GATE-NG-P05-CONTINUITY_PACK_MANDATORY` | P0 | Mandatory continuity pack | Handoff task без pack блокируется |
| Weak Organ Agency | `GATE-NG-P06-ORGAN_VETO_ENFORCEMENT` | P0 | Hard-binding organ checks/veto | Исполнение блокируется при active organ veto |
| Missing Doctrinarium Read Gate | `GATE-NG-P07-DOCTRINARIUM_READ_FIRST` | P0 | Form+Pain read ACK | Без ACK задача не стартует |
| Missing Pain Memory | `GATE-NG-P08-PAIN_PREFLIGHT_REQUIRED` | P0 | Pain registry + preflight injection | Повтор боли ловится pre-task |
| Missing Development Preview | `GATE-NG-P09-DEV_PREVIEW_SCREENSHOT_REQUIRED` | P0 | Preview/screenshot discipline | Без matrix screenshots визуальный task блокируется |
| Resource Burn / KPD Blindness | `GATE-NG-P10-KPD_BUDGET_REQUIRED` | P0 | Pre-task KPD budget + stop threshold | Есть заявка на стоимость и ожидаемую дельту |
| Sovereignty Risk | `GATE-NG-P11-SOVEREIGN_FALLBACK_REQUIRED` | P0 | Local fallback matrix | Критичное действие имеет fallback path |
| External/Freelance Readiness Gap | `GATE-NG-P12-DELIVERABLE_PACKAGE_REQUIRED` | P1 | Delivery package discipline | Нет handoff без package manifest |
| Throne/Custodes Future Gap | `GATE-NG-P13-THRONE_TRANSITION_BOUNDARY` | P1 | Transition criteria checklist | Эскалация в Throne без checklist блокируется |

## 4. Phase plan

### Phase A (дни 1-3)

1. `TASK-20260524-NEWGEN-PAIN-GATE-REGISTRY-INTEGRATION-PC-V0_1`
2. `TASK-20260524-NEWGEN-CURRENT-TRUTH-RECONCILIATION-PC-V0_1`
3. `TASK-20260524-NEWGEN-DOCTRINARIUM-READ-FIRST-ENFORCEMENT-PC-V0_1`

Ожидаемый эффект: stop повторяемых admission ошибок и truth drift.

### Phase B (дни 4-7)

1. `TASK-20260524-NEWGEN-REPO-CLASSIFIER-QUARANTINE-ENFORCEMENT-PC-V0_1`
2. `TASK-20260524-NEWGEN-CONTINUITY-PACK-MANDATORY-HANDOFF-PC-V0_1`
3. `TASK-20260524-NEWGEN-ORGAN-VETO-RUNTIME-BINDING-PC-V0_1`
4. `TASK-20260524-NEWGEN-KPD-BUDGET-PREFLIGHT-PC-V0_1`

Ожидаемый эффект: меньше мусора, меньше потерь контекста, больше управляемости исполнения.

### Phase C (дни 8-14)

1. `TASK-20260525-NEWGEN-DEV-PREVIEW-SCREENSHOT-GATE-PC-V0_1`
2. `TASK-20260525-NEWGEN-VISUAL-CONTRACT-HARD-BLOCK-PC-V0_1`
3. `TASK-20260525-NEWGEN-OWNER-ANSWER-WRITE-PATH-HARDENING-PC-V0_1`
4. `TASK-20260525-NEWGEN-PAIN-MEMORY-LEDGER-INJECTION-PC-V0_1`
5. `TASK-20260525-NEWGEN-EXTERNAL-DELIVERABLE-PACKAGE-POLICY-PC-V0_1`
6. `TASK-20260526-NEWGEN-SOVEREIGN-FALLBACK-MATRIX-PC-V0_1`
7. `TASK-20260526-NEWGEN-THRONE-TRANSITION-CRITERIA-PC-V0_1`

Ожидаемый эффект: системная боль перестает "переписываться", а начинает блокировать и направлять.

## 5. Что не делать в этом roadmap

1. Не заявлять production/autonomy readiness.
2. Не раздувать scope новыми мегапланами до закрытия P0 pain-gates.
3. Не считать report-generation эквивалентом owner-power growth.
4. Не делать visual acceptance без screenshots и evidence binding.

## 6. Exit condition roadmap v0.1

Roadmap v0.1 считается полезным, если:

1. pain-gates зарегистрированы и реально применяются при admission;
2. минимум 3 consecutive tasks закрыты без повтора одной и той же P0 боли;
3. нет generic PASS в owner-facing закрытиях;
4. truth drift (`README`/manifest/current truth) устранен или явно маркирован и контролируется.
