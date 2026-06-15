# Doctrinarium Gate Spine V0.1

This directory contains the first machine-readable read-first spine for NewGen task admission.

## Files

- `declaration_index_v0_1.json`: declaration catalog and task-type read sets.
- `gate_registry_v0_1.json`: active gates, forbidden patterns, pass/fail criteria, evidence requirements.
- `read_first_protocol_v0_1.md`: human protocol for using the spine.
- `TEMPLATES/task_start_doctrinarium_block_v0_1.md`: copy-ready task start block.
- `TOOLS/doctrinarium_preflight_v0_1.py`: task-type preflight resolver.
- `REPORTS/preflight_smoke_report_v0_1.json`: smoke run evidence for v0.1 task types.

## Scope and Boundaries

This is a foundation mechanism only.

Proven:

- Doctrinarium declarations are indexed in machine-readable form.
- Task-type preflight returns required declarations and gates.

Not proven:

- full organ intelligence;
- automatic enforcement across all taskpacks;
- final visual quality;
- production autonomy.
