# NEXT FOCUSED STRIKES V0.1 (DRAFT)

> Цель: короткие локальные удары, которые реально укрепляют clean core, а не расширяют декорации.

## Strike 1: Current Truth Reconciliation

1. Scope: `IMPERIUM_NEW_GENERATION/TRUTH/**`, верхнеуровневые truth declarations.
2. Owner organ: `ADMINISTRATUM + DOCTRINARIUM`.
3. Result: единый reconciliation report `current_vs_historical`, где видно что stale, что current.
4. PASS signal: `CURRENT_TRUTH_ROOT` совпадает с актуальным `HEAD` и корректно маркирует historical snapshots.
5. If skipped: агенты продолжают опираться на устаревшие truth-объекты.

## Strike 2: Operator Cockpit Hard Admission Gate

1. Scope: `SANCTUM_NG/OPERATOR_COCKPIT/**` + contracts.
2. Owner organ: `OFFICIO_AGENTIS + INQUISITION + MECHANICUS`.
3. Result: acceptance gate блокирует cockpit verdict без evidence/path/screenshot consistency.
4. PASS signal: нельзя получить green cockpit verdict при `UNKNOWN/MISSING/FOUNDATION_ONLY`.
5. If skipped: визуальный pseudo-green повторится.

## Strike 3: Owner Answer Write Path (Bounded)

1. Scope: `SANCTUM_NG` owner-question layer.
2. Owner organ: `OFFICIO_AGENTIS + ADMINISTRATUM`.
3. Result: file-backed write канал для owner answer с request/result receipts.
4. PASS signal: вопрос меняет state через проверяемый audit trail, без автономных inference claims.
5. If skipped: owner gate остается read-only и не закрывает цикл управления.

## Strike 4: Organ Directive / Veto Upgrade

1. Scope: `CONTRACTS/ORGAN_*`, `ORGAN_DIALOGUE`, `SERVITOR execution bindings`.
2. Owner organ: `DOCTRINARIUM + INQUISITION + STRATEGIUM`.
3. Result: пакеты органов содержат executable constraints (`required_checks`, `veto_conditions`, `allowed_actions`).
4. PASS signal: Servitor execution нельзя запустить при активном organ veto.
5. If skipped: органы останутся в роли “красивых карточек”.

## Strike 5: Repo Hygiene Classifier + Quarantine

1. Scope: `RUNS`, `REPORTS`, `ARCHIVE`, `TRUTH`.
2. Owner organ: `ADMINISTRATUM + MECHANICUS`.
3. Result: классификация `CANON/CURRENT_TRUTH/RUNTIME/REPORT/ARCHIVE/QUARANTINE`.
4. PASS signal: новые runtime-heavy артефакты не загрязняют core без явной метки и политики хранения.
5. If skipped: сигнал/шум продолжит ухудшаться.

## Strike 6: Freshness-Aware Evidence Indexing

1. Scope: `TRUTH/EVIDENCE_*`, `REPORT_STATUS_INDEX`, cockpit source panels.
2. Owner organ: `ADMINISTRATUM + INQUISITION`.
3. Result: stale evidence автоматически подсвечивается и не может поддержать strict pass.
4. PASS signal: cockpit различает `CURRENT` vs `STALE` для evidence в одном экране.
5. If skipped: старые артефакты продолжат маскироваться под актуальные.

## Strike 7: Continuity Pack Operationalization

1. Scope: `SANCTUM_NG/OPERATOR_COCKPIT/DATA/continuity/**`, tools/contracts.
2. Owner organ: `ADMINISTRATUM + OFFICIO_AGENTIS`.
3. Result: continuity pack не только preview, а стабильный action с manifest и start context.
4. PASS signal: следующий чат стартует с корректным минимальным context pack без ручного сбора.
5. If skipped: каждый новый запуск будет терять контекст и KPD.

## Strike 8: Declared Gate Registry Synchronization

1. Scope: gate declarations in active NewGen operational flow.
2. Owner organ: `DOCTRINARIUM + INQUISITION`.
3. Result: устранение расхождений между “объявленными обязательными gate families” и фактическими registry entries.
4. PASS signal: no orphan mandatory gates in reports/contracts.
5. If skipped: неоднозначность admission правил сохранится.

## Рекомендуемый порядок

1. Strike 1
2. Strike 2
3. Strike 3
4. Strike 4
5. Strike 5
6. Strike 6
7. Strike 7
8. Strike 8

## Принцип исполнения для всех strike-задач

1. один четкий claim boundary;
2. один короткий measurable outcome;
3. scoped verdict;
4. честный `NOT_PROVEN` список;
5. обязательный write-back в truth/gate/memory слой.

