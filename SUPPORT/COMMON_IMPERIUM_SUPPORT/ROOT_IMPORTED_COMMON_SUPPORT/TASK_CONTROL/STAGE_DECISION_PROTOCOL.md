# Stage Decision Protocol V0.1

## Decision options

- ACCEPT: stage output is sufficient and verified.
- REQUEST_FIX: stage requires bounded fixes before continuation.
- CONTINUE_WITH_NOTES: continue while preserving explicit known risks.
- STOP: pause task due to blockers or unsafe uncertainty.
- SPLIT_REQUIRED: split stage/task into narrower admitted work packets.

## Decision contract

Each decision should record:
- decision code;
- short rationale;
- requested next action;
- evidence reference.

## Safety laws

- no fake PASS when blockers exist;
- no continuation without checkpoint for LARGE/MEGA;
- no hidden skip of required phase;
- no claim of completion when key evidence is missing.
