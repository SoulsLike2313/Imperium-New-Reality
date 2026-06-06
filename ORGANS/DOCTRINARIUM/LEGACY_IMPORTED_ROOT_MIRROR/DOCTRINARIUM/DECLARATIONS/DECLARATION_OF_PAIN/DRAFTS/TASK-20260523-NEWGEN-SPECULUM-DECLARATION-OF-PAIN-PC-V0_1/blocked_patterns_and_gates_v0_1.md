# Blocked Patterns and Gates V0.1 (Draft)

Task: `TASK-20260523-NEWGEN-SPECULUM-DECLARATION-OF-PAIN-PC-V0_1`  
Status: `DRAFT / NOT FINAL CANON`  
Verdict target: `PASS_FOR_DECLARATION_OF_PAIN_DRAFT_ONLY`

## 1. Hard-block patterns

Ниже паттерны, которые должны получать `BLOCK` до выполнения repair path.

| Pattern ID | Block pattern | Why blocked | Gate to enforce | Unblock condition |
|---|---|---|---|---|
| `BP-001` | Generic owner-facing `PASS` | Маскирует границы доказанности | `GATE-NG-P03-NO_GENERIC_PASS` | Scoped verdict + `NOT_PROVEN` + `NOT_RUN` |
| `BP-002` | Visual task без contract/screenshot | Повтор визуальной боли | `GATE-NG-P01-VISUAL_CONTRACT_MANDATORY` | Contract + matrix + linter + owner decision |
| `BP-003` | Foundation-only task без owner-visible delta | Наращивает fatigue | `GATE-NG-P00-OWNER_POWER_DELTA_REQUIRED` | Явный cockpit delta и evidence |
| `BP-004` | Start task without Form+Pain read ACK | Drift doctrine | `GATE-NG-P07-DOCTRINARIUM_READ_FIRST` | Form+Pain ACK в preflight |
| `BP-005` | Action button без request/result receipt | Fake operability | `GATE-NG-P06-ORGAN_VETO_ENFORCEMENT` + action receipt policy | Проверяемая request/result цепочка |
| `BP-006` | Repo-heavy артефакты без класса | Засорение truth слоя | `GATE-NG-P04-REPO_CLASSIFICATION_REQUIRED` | Class tag + quarantine policy |
| `BP-007` | Handoff without continuity pack | Потеря контекста | `GATE-NG-P05-CONTINUITY_PACK_MANDATORY` | Pack + manifest + start-here |
| `BP-008` | Pain повторился, но gate не обновлен | Система не учится | `GATE-NG-P08-PAIN_PREFLIGHT_REQUIRED` | Pain register update + preflight injection |
| `BP-009` | KPD-неограниченная задача | Ресурсный burn | `GATE-NG-P10-KPD_BUDGET_REQUIRED` | Pre-task budget + stop threshold |
| `BP-010` | Production/autonomy claim из bounded demo | Суверенный overclaim риск | `GATE-NG-P11-SOVEREIGN_FALLBACK_REQUIRED` | Повторяемые proof-loops + fallback matrix |

## 2. Allowed future tasks (admitted)

Допускать:

1. Задачи, которые закрывают P0 pain classes из matrix.
2. Задачи reconciliation truth (`README`/manifest/current truth).
3. Задачи, которые конвертируют foundation в operator-usable control.
4. Задачи, которые усиливают continuity, pain memory и repo hygiene.
5. Задачи с четким scoped verdict и честным `NOT_PROVEN`.

## 3. Blocked future tasks (until pain closure)

Блокировать:

1. Большие roadmap-расширения без прямого P0 pain reduction.
2. Merge main/test до pain-gate integration и repo-classification discipline.
3. "Финализация визуала" без hard visual gate.
4. Любые задачи с формулировкой "production-ready/autonomous" без строгих proof loops.
5. Задачи, которые создают новые слои, но не добавляют owner-facing control.

## 4. Gate pack for immediate activation

Немедленно активировать как minimum pack:

1. `GATE-NG-P00-OWNER_POWER_DELTA_REQUIRED`
2. `GATE-NG-P03-NO_GENERIC_PASS`
3. `GATE-NG-P04-REPO_CLASSIFICATION_REQUIRED`
4. `GATE-NG-P05-CONTINUITY_PACK_MANDATORY`
5. `GATE-NG-P07-DOCTRINARIUM_READ_FIRST`
6. `GATE-NG-P08-PAIN_PREFLIGHT_REQUIRED`

## 5. Refusal wording standard

При блокировке использовать жесткие и однозначные коды:

1. `BLOCK_OWNER_POWER_NOT_IMPROVED`
2. `BLOCK_GENERIC_PASS_OWNER_FACING`
3. `BLOCK_VISUAL_CONTRACT_MISSING`
4. `BLOCK_CONTINUITY_PACK_MISSING`
5. `BLOCK_REPO_HYGIENE_UNCLASSIFIED`
6. `BLOCK_DOCTRINARIUM_READ_ACK_MISSING`
7. `BLOCK_PAIN_PREFLIGHT_MISSING`
8. `BLOCK_KPD_BUDGET_MISSING`
9. `BLOCK_SOVEREIGN_FALLBACK_MISSING`

## 6. Exit criteria for this blocklist v0.1

Blocklist v0.1 можно смягчать только если:

1. не менее 3 задач подряд закрыты без срабатывания `BP-001..BP-010`;
2. pain gates применяются автоматически и проверяемо;
3. нет противоречия между declared truth и фактическим деревом NewGen.
