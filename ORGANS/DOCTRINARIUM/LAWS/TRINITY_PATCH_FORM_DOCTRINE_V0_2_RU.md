# Доктрина Trinity Patch Form v0_2 (закалённая форма)

Статус: предложение организационной формы. Подчиняется Конституции §13 и Паспорту §2/§5.

## 1. Назначение
Единая форма патч-пака Империума: каждый пак самоописывается, доказывает себя и
откатывается. Никаких декоративных структур (Паспорт §3).

## 2. Канон-закрывающие поля
- authority_refs — какому закону служит патч (>=1).
- scope.in_paths / out_paths — границы записи (validated push, Паспорт §7).
- dirty_scope_expectation — additive_only | classification_only | move_only | mixed.
- forbidden_actions_checked — патч сам декларирует проверенные запреты.
- rollback.backup_root — доказуемый откат (_LOCAL_HANDOFF/PATCH_BACKUPS).
- git_truth.expected_before/after/contour — receipt сильнее памяти (Конституция §4).
- owner_decision_required — минимальное следующее решение владельца (Паспорт §4).

## 3. Форма направлений 5 / 7 / 10 / 14
Патч-пак может нести функции сразу по нескольким направлениям.
Эталон = 14: target_form=14 И declared_count=14 И покрыты все 14 направлений таксономии.
Формы 5/7/10 валидны, но НЕ эталон.

Таксономия 14 направлений:
1 GOVERNANCE · 2 CLEANUP_HYGIENE · 3 PASSPORTING · 4 VALIDATION_PROOF · 5 CONTINUITY ·
6 TOOLING_MECHANICUS · 7 UX_OBSERVABILITY · 8 ROUTING_TASKING · 9 SECURITY ·
10 GHOST_EVOLVE_LEARNING · 11 KNOWLEDGE_SCHOLA · 12 STRATEGY_STRATEGIUM ·
13 EXTERNAL_TRADING · 14 EXTERNAL_FREELANCE_DELIVERY

## 4. Статусы направлений
- active — реально поставлено в этом паке; ОБЯЗАН иметь proof_receipt.
- dormant — объявлено, но не тронуто; ОБЯЗАН иметь dormant_declaration и execution_mode=static.

## 5. Спящая зона (owner decision, 2026-06-14)
EXTERNAL_TRADING и EXTERNAL_FREELANCE_DELIVERY держим в dormant: знаем, не трогаем.
Текущий вектор — высокоценный UI/UX и инженерная чистота (MetaOS, AI-оркестратор).

## 6. Live-gate
execution_mode ∈ {static, sim, paper, shadow, live}.
live ЗАПРЕЩЁН без owner_canon_amendment_ref (forbidden_actions: live_trading_execution,
real_servitor_execution, live_llm). Открытие live — только отдельным owner-approved
canon-amendment паком (README §4, Паспорт §1, Конституция §9/§13).

## 7. Ghost Evolve
Органы учатся сами: self_describe, self_prove, self_heal, self_direct, learning_receipt.
self_direct — всегда owner-gated.
