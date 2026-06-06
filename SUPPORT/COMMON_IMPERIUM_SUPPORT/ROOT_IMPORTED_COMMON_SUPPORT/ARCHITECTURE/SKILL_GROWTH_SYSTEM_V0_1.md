# SKILL GROWTH SYSTEM V0.1

## Purpose
Skill Growth System V0.1 is a New Generation foundation layer that converts bounded task failure/rerun outcomes into reusable learning records:

1. skill gap records
2. lesson records
3. skill update proposals
4. validator recommendation records

This layer is deterministic and evidence-oriented.
It is not a production self-learning runtime.

## Relation to previous phases
Skill Growth System V0.1 is downstream of:

1. Task Kernel / Registry V0.1
2. 8-Organ Scoping Corridor V0.1
3. Servitor Run/Rerun Loop V0.1
4. Task State + Evidence Binder V0.1
5. Visual Brain Task Corridor V0.1

It does not replace these layers.
It consumes their structured failure and rerun outputs.

## Input sources
Primary input categories:

1. failure classifications from run/rerun artifacts
2. rerun decision classes (`RERUN_REQUIRED`, `ASK_OWNER`, `ASK_ORGAN`, and related)
3. bounded evidence references
4. foundation-level policy markers (`FOUNDATION_ONLY`, `NOT_PRODUCTION_EXECUTOR`)

If live records are unavailable, V0.1 uses deterministic foundation samples marked as `FOUNDATION_SAMPLE`.

## Output artifacts
Skill Growth System V0.1 emits:

1. `SKILL_GAP_RECORD` artifacts
2. `SKILL_LESSON_RECORD` artifacts
3. `SKILL_UPDATE_PROPOSAL` artifacts
4. `VALIDATOR_RECOMMENDATION_RECORD` artifacts
5. `SKILL_GROWTH_CYCLE` sample envelope
6. generated growth indexes and catalogs
7. validator report and task report bundle

## Lifecycle: failure to improvement input
The foundation lifecycle is:

1. classify failure or rerun decision
2. map classification to skill gap
3. derive lesson with proof status
4. derive non-mutating skill update proposal
5. derive validator recommendation (advisory by default)
6. emit structured cycle record for future task/agent improvement planning

## No-fake-learning boundary
Allowed claims in V0.1:

1. deterministic generation of learning artifacts from bounded evidence classes
2. explicit confidence/proof status markers
3. advisory, non-mutating skill update proposals

Forbidden claims in V0.1:

1. production self-learning is already active
2. live agent skill mutation is automatic
3. future task success is guaranteed
4. live organ dialogue is proven
5. production autonomous execution is proven

## Integration hooks
### Visual Brain hook
Visual Brain may render skill-growth panels from generated index/cycle data in read-only mode.

### Servitor rerun hook
Servitor rerun policy may consume proposal/recommendation records as advisory inputs for future bounded reruns.

Both integrations are post-foundation and must preserve no-fake-learning laws.

## Foundation-only limitations
V0.1 limitations:

1. no live autonomous learning loop
2. no automatic update application to agent profiles
3. no online reinforcement or production feedback mutation
4. no claim of merge or runtime readiness by this layer alone

This task establishes contracts, deterministic sample artifacts, builder/validator tooling, and evidence surfaces only.
