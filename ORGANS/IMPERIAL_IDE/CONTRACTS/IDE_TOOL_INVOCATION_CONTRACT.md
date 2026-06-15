# IDE Tool Invocation Contract

The IDE must not invoke tools through ungoverned shell calls.

## Invocation Flow

1. IDE extension creates a tool invocation request.
2. Request names a Mechanicus `tool_id`.
3. Mechanicus checks registry and command policy.
4. Default action is dry-run receipt emission.
5. Future real execution requires owner-approved sandbox policy and post-run receipts.
