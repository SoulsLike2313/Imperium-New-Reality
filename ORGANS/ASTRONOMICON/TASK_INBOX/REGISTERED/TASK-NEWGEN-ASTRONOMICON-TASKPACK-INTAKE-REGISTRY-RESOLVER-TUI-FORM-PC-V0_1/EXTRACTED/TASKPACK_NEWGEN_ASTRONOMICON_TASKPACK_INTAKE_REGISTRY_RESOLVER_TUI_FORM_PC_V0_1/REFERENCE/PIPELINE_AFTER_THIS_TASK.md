# Pipeline After This Task

After PC Servitor commits/pushes:

1. Send final commit URL to Inquisitor with `TASKPACK_INQUISITOR_COMMIT_MATRIX_SEMANTIC_REVIEW_V0_1.zip` and phrase `start task`.
2. Send same final commit URL to Speculum with `TASKPACK_SPECULUM_COMMIT_TECHNICAL_REDTEAM_MATRIX_REVIEW_V0_1.zip` and phrase `start task`.
3. Logos-Prime receives reviews and decides whether next task should be:
   - harden Astronomicon resolver further,
   - run first real-use Ghost_Evolve pilot through Astronomicon,
   - or fix organ/task-entry gaps discovered by Stage 2.
