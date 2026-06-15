# OPS INTEGRATION KNOWN FIXES

This file is an execution aid for the Servitor.

## Fix 1: validate_intent contract

Observed candidate issue:

- task_console.validate_intent returns only a problems list.
- CLI classify expects tuple unpacking: ok, problems = validate_intent(intent).
- This causes ValueError.

Required contract:

```python
def validate_intent(intent) -> tuple[bool, list[str]]:
    problems = []
    # existing validation checks
    return (len(problems) == 0), problems
```

All callers must use the same contract.

## Fix 2: integrated path structure

Required destination layout:

```text
ORGANS/IMPERIAL_IDE/OPS/
  ENGINE/imperium_ops/
  CLI/
  TUI/
  TESTS/
```

Preserve ENGINE so CLI and TUI path discovery that expects ../ENGINE continues to work.

If imports are patched instead, record the changed files and prove CLI and TUI smoke.

## Fix 3: Astronomicon-compatible taskpack mode

The taskpack builder must support an Astronomicon-compatible mode that writes:

- MANIFEST.json
- TASK_SPEC.md
- ACCEPTANCE_GATES.md
- OUTPUT_REQUIREMENTS.md
- TASK_ROUTE_MANIFEST_TEMPLATE.json
- TASK_START_ACK_TEMPLATE.json

MANIFEST.json must include:

- schema_version: astronomicon.taskpack.v0_1
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

## Fix 4: validated push policy

Do not use a categorical push ban.

Use:

validated push is allowed and expected after validation, scope check, secret check, and task policy.

## Fix 5: dry-run versus live registration

Keep dry-run registration safe under OPS/STAGING.

Expose live registration as a gated mode targeting:

ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/

Do not use live mode unless safety checks pass and a receipt is written.
