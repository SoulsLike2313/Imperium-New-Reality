# Doctrinarium Read-First Protocol V0.1

Task anchor: `TASK-20260524-NEWGEN-DOCTRINARIUM-GATE-SPINE-READ-FIRST-VM3-V0_1`  
Scope: `IMPERIUM_NEW_GENERATION only`  
Status: `FOUNDATION / PRE-FLIGHT MECHANISM`

## Purpose

This protocol turns Doctrinarium declarations into a machine-readable preflight step that must run before scoped work starts.

Preflight must answer:

1. required documents to read;
2. active gates;
3. forbidden patterns;
4. PASS criteria;
5. FAIL criteria;
6. evidence requirements;
7. not-proven boundary.

## Authority Inputs

Preflight authority sources:

1. `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/declaration_index_v0_1.json`
2. `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/gate_registry_v0_1.json`
3. `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DECLARATIONS/DECLARATION_OF_FORM/IMPERIUM_NEWGEN_DECLARATION_OF_FORM_OWNER_CORRECTED_RU_V0_2.pdf`
4. `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DECLARATIONS/CORE_SYNTHESIS/IMPERIUM_NEWGEN_DOCTRINARIUM_FORM_AND_PAIN_SYNTHESIS_RU_V0_1.pdf`
5. `IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DECLARATIONS/DECLARATION_OF_VISUAL/IMPERIUM_NEWGEN_DECLARATION_OF_VISUAL_POWER_RU_V0_1.pdf`

## Mandatory Start Sequence

Before any file edits:

1. Sync repo to latest `origin/master`.
2. Verify `HEAD`, branch, and remote head truth.
3. Verify clean worktree or stop with explicit dirty report.
4. Run preflight:

```bash
python3 IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TOOLS/doctrinarium_preflight_v0_1.py --task-type <task_type>
```

5. Report preflight output in task start block.
6. Read all required declaration files from preflight output.
7. Confirm scoped PASS/FAIL boundary before edits.

## Supported Task Types

- `core_task`
- `visual_cockpit`
- `tool_acquisition`
- `continuity`
- `repo_hygiene`
- `organ_directive`
- `freelance_external`

## PASS Criteria for Protocol Use

Protocol run is `PASS` only if all are true:

1. preflight JSON is generated for the declared task type;
2. preflight includes declaration read set + active gates + forbidden patterns;
3. preflight includes pass/fail/evidence lists;
4. task start message embeds the Doctrinarium block;
5. scoped verdict is used (`PASS_FOR_<X>_ONLY`), never generic `PASS`.

## FAIL Criteria for Protocol Use

Protocol run is `FAIL/BLOCK` if any are true:

1. task starts without preflight;
2. declaration read set is missing/skipped;
3. active gates are not reported;
4. generic PASS is claimed;
5. green/proved status is claimed without evidence refs.

## Not-Proven Boundary

This protocol does not prove:

- full organ intelligence;
- automatic enforcement across all taskpacks;
- final visual quality;
- production autonomy.

## Output Contract

Preflight output should be retained as JSON in task evidence and include at minimum:

- `task_type`
- `required_declarations`
- `active_gates`
- `forbidden_patterns`
- `pass_criteria`
- `fail_criteria`
- `evidence_required`
- `not_proven_boundary`

## Stop Conditions

Stop and block task start if:

1. declaration index or gate registry cannot be parsed;
2. task type is unsupported;
3. required declaration path is missing;
4. gate registry returns zero gates for a non-trivial task type.
