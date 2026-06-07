# ACCEPTANCE_GATES

## Gate 1: Language
Документация RU, код/идентификаторы EN.

## Gate 2: No-BOM / JSON parse
Все JSON парсятся, BOM нет.

## Gate 3: Compile
`python -m py_compile` по всем .py => COMPILE_OK.

## Gate 4: Smoke
`TESTS/ops_smoke.py` => SMOKE RESULT: PASS (exit 0), 15/15 этапов.

## Gate 5: Admission
`taskpack_builder.admission_precheck` => 0 blockers.

## Gate 6: Safety
Все опасные флаги OFF по умолчанию; push gated.

## Gate 7: Anti-fake-green
Нет PASS без receipt; "зелёнка" без доказательств → HELD.

## Gate 8: Scope
Diff только в ORGANS/IMPERIAL_IDE/OPS/ и STAGING/.

## Gate 9: Full loop
Одна задача проходит все 15 этапов внутри IDE и даёт вердикт.
