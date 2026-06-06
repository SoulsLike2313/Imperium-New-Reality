# TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_3

## Mission

Build Post Work Bundle Admission Ring V0.3 as the standard task completion closure route.

V0.1 proved the first post-work bundle ring and 9-organ receipt frame.
V0.2 added schema-backed checker, closure updater, repair loop, fixtures, and stronger admission checks.
V0.3 must make this a normal completion path for every future task.

The final goal is not another isolated report. The final goal is a runnable and documented closure command/route that turns a registered task into an accepted or blocked bundle through Administratum, 9-organ receipts, Inquisition, Custodes matrix audit, Schola learning, Git closure, and post-push no-write proof.

## Prime intent

Servitor must become a precise executor, not the keeper of all truth.
Internal organs must gather, verify, index, and accept work.
Administratum must not accept final task closure without a valid bundle.
Inquisition must block fake green and contradictions.
Custodes must audit receipt quality and matrix compliance, without claiming full Throne authority.
Schola must turn every learned rule into organ-owned contracts, schemas, templates, validators, receipts, or next-route cards.

## Required first move

Before any mutation, Servitor must:

1. Resolve current Astronomicon expected task.
2. Read the registered taskpack.
3. Read the route manifest and organ participation files.
4. Enter Servitor role through OFFICIO_AGENTIS.
5. Produce an Officio role entry receipt.
6. After OFFICIO role entry, all owner-facing live and final output must be Russian.
7. Machine artifacts remain ENGLISH UTF8 NO_BOM.

## Build scope

Create or update the smallest necessary set of New Reality files for V0.3.

Primary target area:

- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/
- ORGANS/_POST_WORK_RING/
- ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/
- ORGANS/INQUISITION/
- ORGANS/CUSTODES/ORGAN_MATRIX_AUDIT/
- ORGANS/SCHOLA_IMPERIALIS/
- REPORTS/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_3/

## V0.3 required deliverables

1. Standard closure route contract

Create a contract that defines the normal post-task closure path:

- input: task_id
- locate registered taskpack
- locate task reports
- collect organ receipts
- build bundle manifest and bundle index card
- run schema checker
- run Inquisition contradiction scan
- run Custodes organ matrix audit
- run Schola enhanced ghost evolve receipt
- emit repair request on BLOCK
- emit accepted closure only on PASS or PASS_WITH_WARNINGS
- perform git closure and remote proof
- perform post-push no-write proof

2. Standard close command or script

Create a runnable tool such as:

- administratum_standard_task_closure_v0_3.py

The exact name may be adjusted to match repo conventions, but the command must be visible in the report and Mechanicus tool delta.

The command must support at minimum:

- --task-id
- --repo-root
- --reports-dir or auto-discovery
- --receipt-out or output directory
- --mode validate or close, if useful

3. Closure updater V0.3

Improve the V0.2 closure updater or add a V0.3 wrapper so that final remote proof is handled without self-reference fake green.

Required model:

- pre_commit_closure_receipt: allowed to be committed
- committed_bundle_index: allowed to reference pre-commit expected state
- post_push_no_write_proof: produced after push and reported to owner; do not pretend it was inside the pushed commit unless a follow-up index commit is explicitly created
- no_write_final_owner_response: final live proof line from Servitor

4. Repair loop hardening

If any required organ receipt is missing, malformed, BLOCK, or schema-invalid, Administratum must emit a repair request and must not emit accepted final closure.

Required files or equivalent:

- repair_request.schema.json
- repair_request_template.json
- fixture_missing_receipt_blocks
- fixture_malformed_receipt_blocks
- fixture_inquisition_block_requires_repair
- fixture_remote_proof_missing_blocks
- fixture_heavy_artifact_in_git_index_warn_or_block according to policy

5. 9-organ receipt schema enforcement

V0.3 must strengthen or finalize one common receipt schema for the 9-organ ring.

Required organs:

- ASTRONOMICON
- OFFICIO_AGENTIS
- ADMINISTRATUM
- MECHANICUS
- DOCTRINARIUM
- INQUISITION
- STRATEGIUM
- SCHOLA_IMPERIALIS
- CUSTODES

Each receipt must carry at minimum:

- task_id
- organ_id
- matrix_version
- authority_boundary
- verdict
- checked_evidence
- checks
- repair_requests
- missing_items
- forbidden_claims
- created_at_utc

6. Bundle vault and GitHub index split

V0.3 must state and enforce the policy:

- GitHub carries safe indexes, schemas, summaries, hash manifests, and small receipts.
- Heavy bundle payload, screenshots, runtime dumps, private/local evidence, or large artifacts remain local-only unless explicitly admitted.
- The Git index must be sufficient to discover and verify the local bundle by hash and path reference, without storing private payload.

7. Enhanced Ghost Evolve hard rule

Schola receipt must prove that this task taught the organs.

For every important discovered rule, Servitor must choose at least one target:

- organ contract
- schema
- template
- validator/checker
- fixture
- README or read-first file
- next-route card

A final summary-only lesson is not enough.

## Out of scope

- Full semantic truth proof.
- Full Custodes or Throne authority.
- WARP runtime.
- Visual IDE release.
- Large UI rebuild.
- Ancient Empire runtime work.
- Private/local payload publication.

## Expected final owner result

Final owner response must be Russian and include:

1. Step name.
2. Primary report path.
3. Verdict.
4. Commit hash.
5. Remote proof local HEAD == origin/master.
6. Clean worktree proof.
7. Short owner comments.
8. Bundle index path.
9. Whether V0.3 standard closure command is runnable.
10. What next task is recommended.
