# IMPERIUM New Generation Core Strategic Direction V0.1

## Purpose

This file is a strategic orientation document for all future IMPERIUM New Generation agents.

It exists so every agent understands the current scale of work, why Officio Agentis is being hardened first, and what larger system form the project is moving toward.

## Current Priority

The immediate priority is Officio Agentis.

Officio Agentis must become the role, settings, focus, permission, response-contract, and execution-discipline gateway for IMPERIUM agents.

Before Servitor performs serious work, it must be able to query Officio and receive:

1. its role;
2. its mode;
3. its permissions;
4. its forbidden actions;
5. its prompt/task acceptance rules;
6. its response contract;
7. its requirement/evidence obligations;
8. its stop conditions;
9. its scope boundaries;
10. its final Owner response form.

## Why Officio Comes First

The current main failure mode is not that agents cannot work.

The failure mode is that large language model agents often:

- understand the general task;
- complete part of the requested work;
- miss details, visual requirements, or format requirements;
- report confidence too early;
- claim completion without evidence;
- answer in unstable and verbose forms.

Officio must prevent this by converting intent into strict machine-readable behavior contracts.

## Required Servitor Behavior

Servitor is a strict engineering executor.

Servitor must not behave as a casual assistant, storyteller, strategist, or long-form explainer unless explicitly assigned that mode.

Default Servitor response to Owner must be compact:

```text
STEP:
<exact step name>

BUNDLE:
<full absolute path to evidence/response bundle>

VERDICT:
OVERALL: PASS / WARN / BLOCKED / FAIL
REQ-001: DONE / BLOCKED / NOT_DONE
REQ-002: DONE / BLOCKED / NOT_DONE
...

OWNER COMMENTS:
1. <short Russian comment>
2. <short Russian comment>
3. <short Russian comment>
4. <short Russian comment>
```

All long explanations, evidence, logs, screenshots, receipts, and requirement matrices must go into the bundle, not into chat.

## Non-Negotiable Execution Law

If a requirement exists, it must appear in the final requirement matrix.

Every requirement must be one of:

- DONE with evidence;
- BLOCKED with exact blocker and Owner options;
- NOT_DONE with explicit admission.

No silent partial completion is allowed.

No fake green is allowed.

No visual claim is allowed without screenshot or equivalent visual evidence.

No transfer claim is allowed without source path, target path, SHA256, timestamp, and receipt.

No clean Git claim is allowed without `git status --short` evidence.

## Near-Term Path

### Phase 1 — Finish Officio Agentis

Goal: make Officio operational enough that Servitor can query it directly before work.

Required capabilities:

- role-get;
- settings-get;
- prompt/task acceptance policy;
- response contract export;
- requirement matrix discipline;
- compliance checking;
- role/settings packs for Servitor, Logos-Prime, Logos-Speculum;
- stable compact answer forms;
- no scope drift.

### Phase 2 — Verify Direct Servitor ↔ Officio Use

Servitor must prove it can:

1. call Officio;
2. receive its role;
3. receive its settings;
4. acknowledge role/settings;
5. compile or load a requirement matrix;
6. execute only inside allowed scope;
7. produce a stable final response;
8. satisfy compliance checks.

### Phase 3 — Build the Semantic Base of IMPERIUM

After Officio is stable, collect and formalize the meaning of IMPERIUM:

- what IMPERIUM is;
- what each organ means;
- what each organ is allowed to do;
- what each organ is forbidden to do;
- what each organ contributes to the whole system;
- how each organ communicates with the others;
- what lore, truth, and identity must not be violated.

This becomes the identity spine for all future organ-agents.

### Phase 4 — Build the New Generation 10-Organ Agent Core

Inside `IMPERIUM_NEW_GENERATION`, create an ultra-clean structure with configured local Organ-Agents.

Target organs:

1. ADMINISTRATUM_AGENT
2. OFFICIO_AGENTIS_AGENT
3. ASTRONOMICON_AGENT
4. DOCTRINARIUM_AGENT
5. MECHANICUS_AGENT
6. INQUISITION_AGENT
7. CUSTODES_AGENT
8. STRATEGIUM_AGENT
9. SCHOLA_IMPERIALIS_AGENT
10. THRONE_AGENT

Throne must be handled carefully and later, because it has a special control role.

Each organ must receive:

- Base Half;
- Identity Half;
- role/settings profile;
- core command set;
- Rich CLI shell or operator interface;
- inter-organ protocol;
- receipts/reports/checks;
- runtime isolation;
- compliance discipline.

### Phase 5 — Cleanly Mine the Old IMPERIUM

The old repository, old artifacts, scripts, reports, histories, and lessons are not trash.

They are external memory and ore.

New Generation must not blindly merge old material.

It must selectively absorb useful parts through:

- evidence review;
- source classification;
- usefulness scoring;
- dirty/obsolete artifact quarantine;
- script/tool absorption backlog;
- migration receipts.

Rule:

```text
New Generation accepts the best of the old system without importing dirt.
```

### Phase 6 — Add External Boosters

Only after the core organs exist and communicate should IMPERIUM add major external boosters:

- OSINT / External Evidence Intake;
- OSS architecture pattern mining;
- model adapters;
- skill/MCP-like internal capability zones;
- external tool bridges;
- presentation/distribution adapters.

These are external amplifiers, not replacements for the organ core.

### Phase 7 — Sanctum and Freelance Panel

After the agent core is disciplined and useful, return to control surfaces:

- Sanctum as central operator dashboard;
- Freelance Panel for task intake and delivery;
- presentation/dossier generation;
- distribution/export corridor;
- client-ready deliverable packaging.

### Phase 8 — Throne and Borya

Throne is the higher control agent, eventually living on a dedicated Ubuntu notebook with serious capabilities.

Throne communicates with the organ core and external adapters.

Above the process sits the orchestrator called Borya.

Borya must eventually perform the manual cycle currently done by Owner:

1. accept task;
2. route task;
3. request role/settings;
4. transfer prompt packs;
5. launch execution;
6. fetch bundles;
7. verify evidence;
8. route review;
9. return result;
10. continue repair loop until accepted.

## Long-Term Target

IMPERIUM becomes a script-first, focus-driven AI MetaOS.

Its power comes from:

- strict roles;
- strict settings;
- strict evidence;
- clean organ identity;
- controlled inter-agent communication;
- local agent training;
- reusable scripts;
- external evidence intake;
- operator-grade orchestration.

The goal is not to make agents talk more.

The goal is to make agents execute more exactly.
