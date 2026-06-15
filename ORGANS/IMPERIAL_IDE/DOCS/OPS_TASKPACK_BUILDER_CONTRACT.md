# OPS Taskpack Builder Contract

The OPS builder writes Astronomicon-compatible taskpacks with schema astronomicon.taskpack.v0_1.

Required root files:

- MANIFEST.json
- TASK_SPEC.md
- ACCEPTANCE_GATES.md
- OUTPUT_REQUIREMENTS.md
- TASK_ROUTE_MANIFEST_TEMPLATE.json
- TASK_START_ACK_TEMPLATE.json

MANIFEST.json must include:

- schema_version
- task_id
- taskpack_id
- required_organs
- organ_route
- route_manifest_template
- task_start_ack_template
- language_and_encoding_policy.cyrillic_in_taskpack
- git_push_policy
- allowed_write_scope
- forbidden_actions

Generated root files are UTF-8 without BOM and must not contain Cyrillic text.

Validated push is allowed and expected after validation, scope check, secret check, and task policy.
