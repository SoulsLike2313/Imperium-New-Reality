# Start task read order

1. Read `MANIFEST.json`.
2. Read `TASK_SPEC.md`.
3. Read `ACCEPTANCE_GATES.md`.
4. Read `OUTPUT_REQUIREMENTS.md`.
5. Read `020_SCOPE_LOCKS_AND_CAPS.md`.
6. Read `SKILL_REQUIREMENTS/administratum_continuity_pack_skill_contract.md`.
7. Read `HANDOFF_REQUIREMENTS/logos_prime_handoff_contract.md`.
8. Confirm the task was registered through Astronomicon Skill when possible, or record a fallback command registration receipt if the Skill path fails.

Stop if the repo is not at or safely fast-forwardable from `1f0be633b75a44cc9efbfb8de6e9bae43c5c0e30` or if dirty state is unrelated to this task.
