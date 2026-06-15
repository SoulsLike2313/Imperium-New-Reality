# Task Spec - VM3 Astronomicon Registration and Execution Route Proof

Task ID: `TASK-NEWGEN-VM3-ASTRONOMICON-REGISTRATION-AND-EXECUTION-ROUTE-PROOF-UBUNTU-V0_1`

## Background

PC has completed the initial Astronomicon, language, encoding, retention, and backlog hardening sequence.

Current accepted HEAD:
`06ea677b46d40c092cb38ffb883ed8f00a566b25`

VM3 has already been synced manually and verified:
- repo root: `/home/vboxuser3/IMPERIUM_WORK/Imperium-`;
- branch: master;
- HEAD matches expected;
- worktree clean;
- Python 3.12 available;
- Astronomicon tools present.

The Owner now wants all upcoming execution to move to VM3.

## Goal

Prove that VM3 can execute the same IMPERIUM task route that PC used:

```text
taskpack ZIP
-> Astronomicon intake on VM3
-> registered task_id
-> task_id resolver on VM3
-> Servitor starts by TASK_ID + start task
-> 8 organ route acknowledgement
-> useful route proof output
-> commit/push
```

## Required implementation A - VM3 route truth

Record:
- hostname;
- user;
- repo root;
- branch;
- starting HEAD;
- origin/master HEAD;
- worktree clean state;
- Python version;
- Astronomicon tool presence.

Create:
- `vm3_route_truth_probe.json`
- `vm3_route_truth_probe.md`

## Required implementation B - Astronomicon intake proof

Prove:
- taskpack was registered through Astronomicon on VM3;
- admission verdict;
- task_id;
- registered task path;
- extracted task path;
- route manifest path;
- current expected task update;
- language gate result if available.

Create:
- `vm3_astronomicon_intake_proof.json`
- `vm3_astronomicon_intake_proof.md`

## Required implementation C - TASK_ID resolver proof

Run the Astronomicon resolver on VM3 for this task_id.

Create:
- `vm3_task_id_resolution_proof.json`
- `vm3_task_id_resolution_proof.md`

Must include:
- resolved task_id;
- registered task path;
- extracted path;
- route manifest path;
- resolver verdict;
- caps triggered.

## Required implementation D - Role entry and 8-organ route proof

Create:
- `vm3_role_entry_ack.json`
- `vm3_eight_organ_route_receipt.json`
- `vm3_eight_organ_route_receipt.md`

For each organ:
- participation packet path;
- whether reachable;
- what it contributes to this route proof;
- whether any missing authority exists.

## Required implementation E - Useful output

Create:

`VM3_ROUTE_READINESS_SNAPSHOT.md`
`VM3_ROUTE_READINESS_SNAPSHOT.json`

It must answer:
- Is VM3 ready to execute the next block/context optimization task?
- Which route pieces are proven on VM3?
- Which route pieces remain PC-only or unproven?
- Did language and retention gates work on VM3?
- What does VM3 need before second micro-pilot?
- What is the recommended next task?

## Required implementation F - Next pipeline handoff

Create:

`NEXT_PIPELINE_HANDOFF.json`

It must recommend the next task:

`TASK-NEWGEN-BLOCK-SPINE-CONTEXT-PACK-AND-LLM-FOCUS-OPTIMIZATION-VM3-V0_1`

The handoff must say that the next task should define:
- block standard;
- organ block passports;
- protected/editable/runtime zones;
- context pack schema;
- compact organ digests;
- read-order economy;
- task context pack builder;
- improvement request format;
- context bloat detector.

## Required implementation G - Reports and receipts

Recommended report root:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-VM3-ASTRONOMICON-REGISTRATION-AND-EXECUTION-ROUTE-PROOF-UBUNTU-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `vm3_route_truth_probe.json`
- `vm3_route_truth_probe.md`
- `vm3_astronomicon_intake_proof.json`
- `vm3_astronomicon_intake_proof.md`
- `vm3_task_id_resolution_proof.json`
- `vm3_task_id_resolution_proof.md`
- `vm3_role_entry_ack.json`
- `vm3_eight_organ_route_receipt.json`
- `vm3_eight_organ_route_receipt.md`
- `VM3_ROUTE_READINESS_SNAPSHOT.md`
- `VM3_ROUTE_READINESS_SNAPSHOT.json`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `claim_ledger.jsonl`
- `capability_split_receipt.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

Note:
`final_owner_summary_ru.md` is allowed only as Officio-authorized runtime owner-facing output. It must not become machine policy or task instruction.

## Required closure behavior

VM3 Servitor must commit and push admitted canonical changes.

A final report must not end with:
- `PENDING_COMMIT`;
- `PENDING_PUSH_URL`;
- `PENDING_FINAL_GIT_CHECK`.

If changes are not admitted, Servitor must rollback or quarantine them with receipt, or stop with `BLOCKED_PENDING_OWNER_DECISION`.

## Allowed verdicts

- `VM3_ROUTE_PROOF_PASS_WITH_WARNINGS`
- `VM3_ROUTE_PROOF_PARTIAL`
- `VM3_ROUTE_PROOF_BLOCKED`

Clean PASS is forbidden until external review accepts the VM3 route proof.

## Forbidden

No visual IDE.
No WARP activation.
No block/context optimization implementation.
No API/tool arsenal implementation.
No second micro-pilot.
No freelance or trading execution.
No broad refactor.
No private or secret scanning outside canonical safe scope.
No deleting registered taskpack payloads without retention receipt.
No history rewrite.
