# Симуляция Important Six — Wave 2

Задача: `TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1`

Ниже Servitor проходит шесть ключевых органов и получает структурированный ответ:

## 1. DOCTRINARIUM
- Вопрос: Какие законы и gates обязательны сейчас?
- Вердикт: `PASS`
- Применённые правила:
  - `GATE_DOCTRINARIUM_READ_FIRST`
  - `GATE_NO_GENERIC_PASS`
  - `GATE_NO_GREEN_WITHOUT_EVIDENCE`
  - `GATE_NOT_PROVEN_BOUNDARY`
- Обязательные действия:
  - Run and store preflight output before edits
  - Bind final verdict to scoped Wave 1 slice only
- Запрещённые действия:
  - Claim complete Important Six
  - Claim production autonomy
- Требуемые доказательства:
  - `doctrinarium_preflight_output.json`
  - `applicable_doctrinarium_gates.json`
  - `FINAL_REPORT.md`
  - `closure_receipt.json`
  - `wave1_organ_tui_smoke_report.json`
  - `organ_interaction_simulation_v0_1.json`
- Источник: `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1/sim_query_doctrinarium.json`

## 2. OFFICIO_AGENTIS
- Вопрос: Какие role/language/response правила обязательны?
- Вердикт: `PASS`
- Применённые правила:
  - `GATE_ROLE_ACK_REQUIRED`
  - `GATE_OWNER_LANGUAGE_RU`
  - `GATE_SCOPED_VERDICT_ONLY`
  - `GATE_STOP_CONDITION_BINDING`
- Обязательные действия:
  - Publish officio role contract ack before edits
  - Use scoped verdict format PASS_FOR_<SLICE>_ONLY
- Запрещённые действия:
  - Use generic PASS verdict
  - Continue after Owner Verdict Needed signal
- Требуемые доказательства:
  - `officio_role_contract_ack.json`
  - `taskpack_scope_ack.json`
  - `FINAL_REPORT.md`
  - `closure_receipt.json`
  - `organ_route_plan.json`
- Источник: `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1/sim_query_officio.json`

## 3. ASTRONOMICON
- Вопрос: Как регистрировать, классифицировать и стейджить задачу?
- Вердикт: `PASS`
- Применённые правила:
  - `GATE_ASTRA_TASK_REGISTRATION_REQUIRED`
  - `GATE_ASTRA_STAGE_ROUTE_REQUIRED`
  - `GATE_ASTRA_OWNER_PASS_FAIL_REQUIRED`
  - `GATE_ASTRA_ACTIVE_ARCHIVE_TRANSITION`
- Обязательные действия:
  - Register task packet with class and stage structure
  - Bind owner comments and pass/fail criteria before execution
  - Produce route/stage plan and archive transition rule
- Запрещённые действия:
  - Skip task registration
  - Run stage flow without explicit classification
  - Mark task complete with no archive transition criteria
- Требуемые доказательства:
  - `taskpack_scope_ack.json`
  - `organ_route_plan.json`
  - `important_six_interaction_simulation_v0_1.json`
  - `important_six_interaction_simulation_ru.md`
  - `FINAL_REPORT.md`
  - `closure_receipt.json`
- Источник: `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1/sim_query_astronomicon.json`

## 4. ADMINISTRATUM
- Вопрос: Какая последовательность истории/continuity/evidence обязательна?
- Вердикт: `PASS`
- Применённые правила:
  - `GATE_TASK_REGISTRATION_CONTINUITY`
  - `GATE_EVIDENCE_PACKAGE_REQUIRED`
  - `GATE_REPO_HYGIENE_BOUNDARY`
  - `GATE_SEQUENCE_DISCIPLINE`
- Обязательные действия:
  - Publish final report and closure receipt with evidence paths
  - Verify clean worktree and remote sync after push
- Запрещённые действия:
  - Hide dirty state or missing receipts
  - Claim pass without smoke evidence
- Требуемые доказательства:
  - `taskpack_scope_ack.json`
  - `organ_route_plan.json`
  - `FINAL_REPORT.md`
  - `closure_receipt.json`
  - `wave1_organ_tui_smoke_report.json`
  - `git status --short`
  - `git diff --name-only`
- Источник: `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1/sim_query_administratum.json`

## 5. MECHANICUS
- Вопрос: Какие инструменты и capability truth нужны?
- Вердикт: `PASS`
- Применённые правила:
  - `GATE_RICH_MANDATORY_FOR_WAVE1_TUI`
  - `GATE_CONTROLLED_CAPABILITY_ACQUISITION`
  - `GATE_SCRIPT_ARTIFACT_PRESERVATION`
  - `GATE_COMMAND_CHUNKING_DISCIPLINE`
- Обязательные действия:
  - Probe Rich import and version
  - Store capability registry evidence under Mechanicus TOOLS_REGISTRY
- Запрещённые действия:
  - Claim TUI visual pass with plain fallback only
  - Perform uncontrolled package installs
- Требуемые доказательства:
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS_REGISTRY/tool_capability_registry.json`
  - `IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS_REGISTRY/install_receipts/`
  - `wave1_organ_tui_smoke_report.json`
  - `FINAL_REPORT.md`
  - `closure_receipt.json`
- Источник: `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1/sim_query_mechanicus.json`

## 6. INQUISITION
- Вопрос: Какие fake-green/dirty/duplicate/semantic риски нужно закрыть?
- Вердикт: `BLOCK`
- Применённые правила:
  - `GATE_INQ_NO_FAKE_GREEN`
  - `GATE_INQ_DIRTY_WORK_DETECTION`
  - `GATE_INQ_DUPLICATE_AND_HERESY_CHECK`
  - `GATE_INQ_SPECULUM_HARD_AUDIT`
- Обязательные действия:
  - Run anti-fake-green and evidence-reference checks
  - Check for dirty work and duplicate drift
  - Enforce readability and explainability of closure artifacts
  - Apply hard Speculum-style audit gate before PASS
- Запрещённые действия:
  - Claim PASS without evidence chain
  - Ignore dirty or duplicate findings
  - Ignore semantic contradiction in owner-facing output
- Требуемые доказательства:
  - `wave2_organ_tui_smoke_report.json`
  - `closure_receipt.json`
  - `git_diff_paths`
  - `FINAL_REPORT.md`
  - `important_six_interaction_simulation_v0_1.json`
  - `json_parse_validation_report.json`
- Источник: `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1/sim_query_inquisition.json`

## Вывод по симуляции
- Servitor получил рабочий ask/warn/block профиль по всем 6 органам.
- Route подтверждён как foundation Important Six (Wave 2).
- Границы явно сохранены: без заявлений о production autonomy и полном organ intelligence.
