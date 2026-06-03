# Start task read order

Read these files in order before touching repo files:

1. MANIFEST.json
2. TASK_SPEC.md
3. ACCEPTANCE_GATES.md
4. OUTPUT_REQUIREMENTS.md
5. 020_SCOPE_LOCKS_AND_CAPS.md
6. 030_EXECUTION_PLAN.md
7. INPUTS/previous_stage2_result_synthesis.json
8. INPUTS/admission_positive_controls_seed.json
9. INPUTS/review_synthesis_from_owner_provided_external_reviews.json
10. SCHEMAS/cap_closure_decision.schema.json
11. SCHEMAS/independent_replay_receipt.schema.json
12. SCHEMAS/external_finalization_receipt.schema.json

Then resolve the registered TASK_ID through Astronomicon before execution. Do not execute from the ZIP path alone.
