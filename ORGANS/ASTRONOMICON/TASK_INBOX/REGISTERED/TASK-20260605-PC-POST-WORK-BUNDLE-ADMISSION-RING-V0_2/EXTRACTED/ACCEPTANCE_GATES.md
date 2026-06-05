# Acceptance Gates for TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2

## Gate A: Officio role entry

PASS only if:
- OFFICIO role entry receipt exists.
- Servitor acknowledges active root, task id, and role.
- Owner-facing final output is Russian.
- Machine artifacts remain ENGLISH UTF8 NO_BOM.

## Gate B: Schema enforcement

PASS only if V0.2 checker validates all required schema-backed files:
- bundle manifest,
- bundle index card,
- receipt index,
- file delta index,
- 9-organ ring receipt,
- organ receipt schema,
- repair request schema.

## Gate C: 9-organ receipt ring

Required organs:
- ASTRONOMICON
- OFFICIO_AGENTIS
- ADMINISTRATUM
- MECHANICUS
- DOCTRINARIUM
- INQUISITION
- STRATEGIUM
- SCHOLA_IMPERIALIS
- CUSTODES

PASS only if all required organ ids are represented in the ring receipt.

## Gate D: Repair loop

PASS only if:
- a fixture with a required organ BLOCK creates a repair request,
- final bundle acceptance is blocked while any required BLOCK remains,
- a repair-loop PASS fixture exists after the defect is repaired.

## Gate E: Administratum bundle acceptance

PASS only if:
- Administratum checker report exists,
- issue count and block count are explicit,
- no fake final PASS is possible when schema validation fails,
- bundle index and receipt index can be used as GitHub-safe index.

## Gate F: Inquisition contradiction scan

PASS only if:
- Inquisition receipt checks final report vs git closure vs remote proof.
- PASS_WITH_WARNINGS is not summarized as simple PASS.
- Known caps are preserved.

## Gate G: Custodes narrow audit

PASS only if:
- Custodes checks quality/completeness of organ receipts.
- Custodes does not claim full Throne authority.
- Custodes does not repeat all organ work; it audits the checkers.

## Gate H: Enhanced Ghost Evolve

PASS only if:
- Schola receipt states ULTIMATE_ORGAN_TEACHING.
- At least three learned rules are converted into durable artifacts.
- Learning is not summary-only.
- Any new script/tool is reflected in Mechanicus tool delta.

## Gate I: Closure

PASS only if:
- git status is clean before final response,
- commit is created,
- normal non-force push is done,
- local HEAD equals origin/master after push,
- final remote proof is reported.

## Stop conditions

Stop and report BLOCK if:
- active root is not E:/IMPERIUM_NEW_GENERATION_NEW_REALITY,
- task id mismatch,
- JSON schema validation cannot run and no limitation receipt exists,
- any required organ BLOCK remains,
- git push is unavailable,
- working tree cannot be made clean without unrelated mutation,
- checker reports final acceptance but missing required receipts.
