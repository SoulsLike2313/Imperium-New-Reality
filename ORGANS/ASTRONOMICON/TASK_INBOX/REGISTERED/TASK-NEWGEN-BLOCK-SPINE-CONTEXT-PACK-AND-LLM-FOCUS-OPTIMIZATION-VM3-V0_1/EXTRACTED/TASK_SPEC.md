# Task Spec - Block Spine, Context Pack, and LLM Focus Optimization

Task ID: `TASK-NEWGEN-BLOCK-SPINE-CONTEXT-PACK-AND-LLM-FOCUS-OPTIMIZATION-VM3-V0_1`

## Background

VM3 route proof has been accepted with warnings at head:

`1847fed077a451568904cb8267650cc863d1c7f1`

The Owner now wants the first construction step toward an adaptive block architecture and future IDE workbench.

The immediate goal is not to build a visual IDE. The immediate goal is to make IMPERIUM better at focusing Servitor and large LLMs:
- exact maps;
- compact context packs;
- protected zones;
- organ passports;
- matrix-driven criteria;
- script-first builders;
- bloat detection;
- improvement request loops.

## Core concept

IMPERIUM must not be a repository that agents browse freely.

IMPERIUM must be a block-governed organism that gives agents:
- exact task route;
- exact organ maps;
- exact context pack;
- exact allowed tools;
- exact forbidden zones;
- exact outputs;
- exact validation requirements;
- exact improvement request format.

## Block hierarchy

Define the following hierarchy:

1. `IMPERIUM_CORE_BLOCK`
   - focuses Servitor and large LLMs;
   - issues task context packs;
   - defines allowed organs, tools, APIs, caps, and outputs.

2. `ASTRONOMICON_INTAKE_BLOCK`
   - accepts taskpack ZIP;
   - validates language/encoding/admission requirements;
   - registers task;
   - creates task route and launch card;
   - tells Servitor where to go and why.

3. `ORGAN_BLOCK`
   - each active organ is a local AI-agent/block;
   - each organ contains scripts, files, receipts, visuals/assets, schemas/contracts, matrices, memory, pain memory, success memory, protected zones, and improvement requests.

4. `EXTERNAL_ENHANCEMENT_BLOCK`
   - future API, CLI, browser, local model, tool, or service block;
   - must have a passport, risk profile, resource budget, command/API surface, and use receipt.

5. `IDE_WORKBENCH_BLOCK`
   - future workbench and command room;
   - must display blocks, tools, tasks, context packs, receipts, terminals, browser chambers, resource status, and launch cards.

## Required implementation A - Block standard

Create block standard artifacts, recommended paths:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/BLOCK_STANDARD/BLOCK_STANDARD_V0_1.md`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/BLOCK_STANDARD/BLOCK_STANDARD_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/SCHEMAS/block_manifest.schema.json`

The standard must define:
- block id;
- block type;
- owner organ;
- purpose;
- read-first files;
- protected zones;
- editable zones;
- runtime zones;
- input contracts;
- output contracts;
- scripts/tools;
- receipts;
- matrices;
- memory;
- pain memory;
- success memory;
- improvement requests;
- validation gates;
- context budget.

## Required implementation B - Organ block passports

Create minimal organ block passport skeletons for all 8 active organs.

Recommended paths:

`IMPERIUM_NEW_GENERATION/ORGANS/<ORGAN>/BLOCK/PASSPORT/ORGAN_BLOCK_PASSPORT_V0_1.md`
`IMPERIUM_NEW_GENERATION/ORGANS/<ORGAN>/BLOCK/PASSPORT/ORGAN_BLOCK_PASSPORT_V0_1.json`
`IMPERIUM_NEW_GENERATION/ORGANS/<ORGAN>/BLOCK/READ_FIRST_COMPACT.md`
`IMPERIUM_NEW_GENERATION/ORGANS/<ORGAN>/BLOCK/CONTEXT_DIGEST_V0_1.md`

Each passport must answer:
- what this organ/block does;
- when Servitor should read it;
- what files are mandatory;
- what files are optional;
- what zones are protected;
- what outputs it can provide to a task;
- what improvement requests it can generate;
- which other organs support it.

Keep these skeletons compact. Do not copy large old rules into every passport.

## Required implementation C - Context pack schema and builder prototype

Create:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/CONTEXT_PACKS/TASK_CONTEXT_PACK_SCHEMA_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/CONTEXT_PACKS/TASK_CONTEXT_PACK_TEMPLATE_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/TOOLS/build_task_context_pack_v0_1.py`

The builder prototype must:
- accept a task_id;
- read Astronomicon route manifest if available;
- collect compact organ digests;
- include only mandatory context by default;
- list optional context separately;
- include protected zones;
- include allowed tools placeholder;
- include expected outputs;
- include required receipts;
- produce a JSON context pack and Markdown summary;
- record estimated file count and character count.

The builder may be a prototype, but it must be executable and tested on at least the current registered VM3 task or a synthetic fixture.

## Required implementation D - Read-order economy and bloat detector

Create:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/TOOLS/context_bloat_detector_v0_1.py`

The detector must check:
- task context pack file count;
- approximate character count;
- duplicate read-first entries;
- forbidden broad-read patterns;
- missing compact digest;
- missing protected zone declaration;
- missing expected output declaration.

Create:
- `context_bloat_detector_report.md`
- `context_bloat_detector_receipt.json`

## Required implementation E - Adaptive Matrix Spine updates

Update or create matrices:

`BLOCK_MATURITY_MATRIX`
`CONTEXT_PACK_ECONOMY_MATRIX`
`ORGAN_BLOCK_PASSPORT_MATRIX`
`SERVITOR_LLM_FOCUS_MATRIX`
`IDE_WORKBENCH_REQUIREMENTS_MATRIX`

Each matrix must include:
- criterion id;
- owner organ;
- evidence required;
- PASS/WARN/BLOCK logic;
- score or delta field;
- cap mapping;
- remediation path;
- what useful improvement it forces.

The goal is not many decorative criteria. The goal is adaptive criteria that help Servitor understand what it must do and how to improve IMPERIUM.

## Required implementation F - Ghost_Evolve block learning

Create:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/GHOST_EVOLVE/GHOST_EVOLVE_BLOCK_LEARNING_RULES_V0_1.md`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/GHOST_EVOLVE/GHOST_EVOLVE_BLOCK_LEARNING_RULES_V0_1.json`

It must define:
- how a block records pain memory;
- how a block records success memory;
- how a block creates an improvement request;
- how a block asks a large LLM/Servitor to improve it;
- how a task records whether it increased block usefulness;
- how to compute efficiency delta without fake-green.

## Required implementation G - Improvement request schema

Create:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IMPROVEMENT_REQUESTS/BLOCK_IMPROVEMENT_REQUEST_SCHEMA_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IMPROVEMENT_REQUESTS/BLOCK_IMPROVEMENT_REQUEST_TEMPLATE_V0_1.json`

Each request must include:
- source block;
- pain;
- evidence;
- requested improvement;
- expected output;
- risk;
- owner organ;
- support organs;
- validation needed;
- context needed from Servitor or large LLM;
- success criteria.

## Required implementation H - Future IDE workbench requirements only

Create design contracts only. Do not implement IDE.

Recommended paths:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/IDE_WORKBENCH_REQUIREMENTS_V0_1.md`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/IDE_WORKBENCH_REQUIREMENTS_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/TOOL_CHAMBER_SURFACE_CONTRACT_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/VISIBLE_FOG_MODE_CONTRACT_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/RESOURCE_GOVERNOR_REQUIREMENTS_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/IDE_TECH_STACK_CANDIDATES_V0_1.json`

Must include:
- TypeScript + React frontend candidate;
- Tauri + Rust desktop shell primary candidate;
- Electron fallback candidate;
- local validator policy: Mechanicus validators perform compile/lint/type checks;
- central interactive chamber concept;
- left block/repo explorer concept;
- right tool/API arsenal concept;
- launch card for PC/VM2/VM3 contours;
- visible workbench mode;
- fog/backend mode;
- resource governor requirements;
- browser chamber candidate;
- AdsPower API adapter candidate as normal product API adapter, not bypass/malware tooling.

## Required implementation I - Tool surface candidate cards

Create candidate cards only:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/CANDIDATES/ADSPOWER_API_ADAPTER_CANDIDATE_V0_1.json`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/CANDIDATES/BROWSER_AUTOMATION_CHAMBER_CANDIDATE_V0_1.md`
`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/IDE_WORKBENCH/CANDIDATES/MECHANICUS_LOCAL_VALIDATOR_CANDIDATE_V0_1.json`

Rules:
- no installation;
- no API keys;
- no ToS-bypass objectives;
- no stealth/malware framing;
- no browser automation implementation;
- candidate cards only.

## Required implementation J - Reports and receipts

Recommended report root:

`IMPERIUM_NEW_GENERATION/BLOCK_SPINE/REPORTS/TASK-NEWGEN-BLOCK-SPINE-CONTEXT-PACK-AND-LLM-FOCUS-OPTIMIZATION-VM3-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `block_standard_report.md`
- `organ_block_passport_report.md`
- `context_pack_builder_report.md`
- `context_pack_builder_receipt.json`
- `context_bloat_detector_report.md`
- `context_bloat_detector_receipt.json`
- `matrix_spine_adaptive_update_report.md`
- `ghost_evolve_block_learning_report.md`
- `ide_workbench_requirements_report.md`
- `tool_surface_candidate_report.md`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `claim_ledger.jsonl`
- `capability_split_receipt.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

Note:
`final_owner_summary_ru.md` is allowed only as Officio-authorized runtime owner-facing output. It must not become machine policy or task instruction.

## Required closure behavior

VM3 Servitor must commit and push admitted canonical changes.

A final report must not end with:
- `PENDING_COMMIT`;
- `PENDING_PUSH_URL`;
- `PENDING_FINAL_GIT_CHECK`.

If changes are not admitted, Servitor must rollback or quarantine them with receipt, or stop with `BLOCKED_PENDING_OWNER_DECISION`.

## Allowed verdicts

- `BLOCK_SPINE_CONTEXT_OPTIMIZATION_PASS_WITH_WARNINGS`
- `BLOCK_SPINE_CONTEXT_OPTIMIZATION_PARTIAL`
- `BLOCK_SPINE_CONTEXT_OPTIMIZATION_BLOCKED`

Clean PASS is forbidden until external review accepts the block spine.

## Forbidden

No full IDE implementation.
No desktop app build.
No Tauri or Electron project generation.
No external API integration.
No AdsPower runtime integration.
No browser automation implementation.
No WARP activation.
No second micro-pilot.
No freelance or trading execution.
No broad refactor.
No private or secret scanning outside canonical safe scope.
No deleting registered taskpack payloads without retention receipt.
No history rewrite.
