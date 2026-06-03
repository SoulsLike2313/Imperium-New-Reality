# План становления 8 органов, Astronomicon Task Entry и IDE Release

Status: `LOGOS_PRIME_PLAN_CANDIDATE_V0_1`

## 0. Смысл

Ghost_Evolve V2 уже ввёл Matrix Spine, organ read-first packets, claim ledger, capability split, red-team, review loop, external finalization и cap semantics.

Следующий вектор: IMPERIUM должен стать рабочим организмом, где Servitor входит через IMPERIUM, задача живёт в Astronomicon, все 8 органов участвуют, а IDE позже отображает реальную работу, а не сырые колонки.

## 1. Stage 0 — Receipt Sanitation Closeout

Цель: закончить proof hygiene настолько, чтобы не строить Stage 1 на мутных receipts.

Выход:
- receipt producer inventory;
- migration priority matrix;
- legacy field checker;
- Stage 0 closeout report;
- surviving caps list.

Условие выхода:
- нет неразобранных P0 producer risks;
- есть план P1/P2 миграции;
- Inquisitor + Speculum согласны, что Stage 1 можно начинать с warnings.

## 2. Stage 1 — Eight Organ Mobilization V0.1

Органы:
- Doctrinarium
- Officio Agentis
- Astronomicon
- Administratum
- Mechanicus
- Inquisition
- Strategium
- Schola Imperialis

Каждый орган получает:
- `READ_FIRST_TASK_PARTICIPATION.md`
- `TASK_PARTICIPATION_CONTRACT.json`
- `ORGAN_TASK_INPUTS_OUTPUTS.json`
- `ORGAN_MATRIX_RESPONSIBILITIES.json`
- `ORGAN_TOOL_AND_RECEIPT_INVENTORY.json`
- `ORGAN_IDE_DISPLAY_MODEL.json`
- `KNOWN_GAPS_AND_NEXT_HOOKS.md`

Минимальная роль:
- Doctrinarium: laws, canon/candidate status, forbidden claims.
- Officio: role, language, answer format, agent mode.
- Astronomicon: task location, task ID, stage/route/start protocol.
- Administratum: continuity, receipts, evidence, history.
- Mechanicus: tools, validators, replay, script-first capability.
- Inquisition: caps, fake-green, red-team, downgrade.
- Strategium: priority, expected delta, why this task matters.
- Schola: lesson, KPD, reuse pattern.

## 3. Stage 2 — Astronomicon Task Entry Corridor V0.1

Target Owner workflow:
1. Logos provides taskpack.
2. Owner downloads it.
3. Owner places/unpacks it into Astronomicon task inbox.
4. Owner gives Servitor only task ID and writes `start task`.
5. Servitor finds the task, reads AGENTS.md, Matrix Spine, organ participation files, then starts.

Required:
- task inbox structure;
- task ID resolver;
- task route manifest;
- taskpack admission receipt;
- task start ACK;
- missing task handler;
- duplicate task ID handler;
- simple Owner instructions.

## 4. Stage 3 — First Real-Use Ghost_Evolve Pilot

Goal: run a small real useful task through the 8-organ/Astronomicon entry corridor.

Not WARP. Not freelance production. Not big IDE.

Success:
- 8 organs participate;
- task starts through Astronomicon ID;
- Servitor produces claim ledger, capability split, red-team, receipts;
- Inquisitor/Speculum review same target manifest;
- Logos builds next pipeline faster than before.

## 5. Stage 4 — Agent Harness Data Model for IDE

Define what IDE should show:
- current task;
- organ participation state;
- organ readiness;
- matrix/cap status;
- receipt chain;
- replay status;
- review loop status;
- next pipeline;
- Owner questions;
- runtime output classification;
- evidence bundle.

Required:
- `AGENT_HARNESS_VIEW_MODEL.json`
- organ panel models;
- task corridor state model;
- review loop model;
- evidence/receipt timeline model;
- action socket list.

## 6. Stage 5 — IDE Visual Release V0.1

Principles:
- not default-looking;
- not raw columns;
- no fake buttons;
- shows real state;
- dark sci-fi / expensive / readable;
- every visual claim maps to data.

Possible zones:
- central task corridor;
- 8 organ ring / organ work surfaces;
- matrix/cap strip;
- evidence timeline;
- review tribunal panel;
- Owner action/question panel;
- tool/replay console;
- next pipeline panel.

## 7. Stage 6 — Big Checkup

Questions:
- did task time reduce?
- did ambiguity reduce?
- did Servitor ask fewer bad questions?
- did Inquisitor/Speculum find fewer repeated issues?
- did each task gift measurable efficiency?
- does Owner understand state faster?
- are organs becoming useful work surfaces?

## 8. Doctrine

Receipts are hygiene, not the goal.

The real goal: Servitor enters IMPERIUM, uses 8 organs, works through Astronomicon, improves the organism each task, and later IDE visualizes that living harness.
