# OPS Astronomicon Live Registration Gate

Dry-run registration is active now and writes to:

ORGANS/IMPERIAL_IDE/OPS/STAGING/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/

Live registration target is:

ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/

Live mode remains gated in this task. It must not be enabled until a future gate proves:

- generated taskpack admission precheck passes;
- command policy allows the registration action;
- no secrets or local configs are staged;
- no runtime paths are staged;
- exact write target is inside ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/;
- a live registration receipt is written;
- Owner task policy allows the action.

The current --real CLI path reports a structured blocker instead of writing to the live inbox.
