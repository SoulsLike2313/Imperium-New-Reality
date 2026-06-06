# TASK CONTROL V0.1

This directory defines the first control layer for task volume and stage checkpoints.

It provides:
- volume classes and risk rules;
- machine-readable schemas;
- stage checkpoint protocol;
- owner decision protocol;
- examples for Servitor and active organs.

Core rules:
- scope and volume are independent controls;
- LARGE and MEGA tasks require staged checkpoints;
- skipped phases must be marked BLOCKED or DEFERRED;
- no fake PASS without evidence.

References:
- TASK_VOLUME_CONTROL.md
- TASK_VOLUME_CONTROL.schema.json
- STAGE_CHECKPOINT_PROTOCOL.md
- STAGE_CHECKPOINT.schema.json
- STAGE_DECISION_PROTOCOL.md
