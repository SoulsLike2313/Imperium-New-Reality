# TASK_SPEC

## Task ID
TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-TASK-CONSOLE-AND-TASKPACK-BUILDER-PC-V0_1

## Goal
Сделать Imperial IDE рабочей: владелец пишет задачу человеческим языком и
закрывает полный цикл внутри IDE, без ручных ZIP.

## Scope
ORGANS/IMPERIAL_IDE/OPS/ + STAGING/ (dry-run). Kernel не трогается.

## Компоненты
1. Task Console — создание задачи, тип/scope/risk/organs/push.
2. Taskpack Builder — MANIFEST/SPEC/GATES/OUTPUT/ROUTE/ACK + zip + sha256 + precheck.
3. Astronomicon registration — регистрация командой/кнопкой (dry-run STAGING).
4. Launch Card — карточка запуска + start message.
5. Servitor handoff — передача задачи (real execution blocked).
6. MetaOS route preview, Mechanicus preflight.
7. Validation + receipts + Administratum bundle gate + Inquisition anti-fake-green.
8. Git closure (commit/push или объяснение почему нельзя).
9. Reports/receipts live tracking.

## Lifecycle (15 этапов)
intent_capture, classification, metaos_route_preview, mechanicus_policy_check,
taskpack_generation, astronomicon_registration, launch_card, servitor_handoff,
validation, receipts, administratum_bundle_gate, inquisition_fake_green_check,
owner_summary, git_closure, next_task_recommendation.
