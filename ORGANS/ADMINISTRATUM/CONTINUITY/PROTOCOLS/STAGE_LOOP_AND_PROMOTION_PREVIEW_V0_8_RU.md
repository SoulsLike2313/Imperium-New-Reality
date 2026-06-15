# Stage Loop and Promotion Preview v0.8

Цель: превратить Web Sanctum из cockpit в полный цикл задачи.

## Канон

Taskpack -> Astronomicon admission -> WARP -> Administratum stage receipts -> Astronomicon stage gates -> Inquisition validation -> Report bundle -> Owner review -> Promotion preview.

## Запреты

- Web Sanctum не открывает commit/push.
- Promotion Preview ничего не stage/commit/push.
- Runtime/evidence пишутся в LOCAL_HANDOFF/WARP_RUNS.
- Source repo остаётся только source-кодом.

## Стадии

1. task_admitted
2. work_started
3. implementation
4. validation
5. report_bundle
6. owner_review
7. promotion_ready

Каждая стадия закрывается только через receipt + gate.
