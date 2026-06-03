# TASK SPEC

## Task ID

`TASK-NEWGEN-ADMINISTRATUM-CONTINUITY-ROLE-PACK-AND-LOGOS-OWNER-AUDIT-CARD-CONTRACT-PC-V0_1`

## Step name

Administratum continuity role-pack bridge and Logos Owner Audit Card contract.

## Purpose

Create a repository-backed contract for the Owner-approved Logos review format named `Owner Audit Card`.

This format is used when the Owner gives a Servitor screenshot, review bundles, or task output and says `check`, `verify`, or provides no extra instruction. The assistant must review the work using an optimized, evidence-first card:

1. Trigger.
2. Quick verdict table.
3. What was accepted.
4. What remains risky or not accepted.
5. Short conclusion.
6. Exactly two short paragraphs about what the next task should give.

Also connect this review format to Administratum continuity packs and role-specific handoff packs.

## Strategic direction

Continuity pack selection must support a recipient target:

- `LOGOS_PRIME`
- `INQUISITOR`
- `SPECULUM`

The core continuity truth must remain the same for all recipients. Role behavior must be supplied as a separate clean role pack.

## Required ownership

- Administratum owns continuity pack truth, handoff bundles, source index, history, and current state.
- Officio Agentis owns role packs and response contracts.
- Inquisition owns clean-context and fake-continuity checks.
- Mechanicus validates schemas, manifests, and generated receipts.
- Astronomicon contributes current task route, task registry state, and next task context.
- Doctrinarium stores the binding law if the worker creates a law artifact.
- Schola Imperialis may receive a learning card for the accepted review format.

## Required implementation

Create or update repo artifacts under appropriate organ-owned paths. Prefer paths under:

- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/SKILLS/CONTINUITY_PACK_SKILL/`
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/CONTRACTS/`
- `IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/RESPONSE_CONTRACTS/`
- `IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/ROLE_PACKS/`
- `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/GUARDS/`
- `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/VALIDATION/`
- `IMPERIUM_NEW_GENERATION/ORGANS/SCHOLA_IMPERIALIS/LEARNING_CARDS/`

If exact directories differ, use nearest existing NewGen organ paths and write receipts explaining the chosen paths.

## Owner Audit Card required sections

Represent the format in an easy-to-record Markdown table form plus a short template.

Required sections:

| Order | Section | Content |
| --- | --- | --- |
| 0 | Trigger | Why this review mode was entered. |
| 1 | Quick verdict | Step, verdict, final head, git closure, main accepted result, clean pass status. |
| 2 | Accepted evidence | What is accepted and why it matters. |
| 3 | Concerns | Remaining caps, risks, stale receipts, missing proof, or scope exclusions. |
| 4 | Logos conclusion | Short engineering conclusion. |
| 5 | Next task value | Exactly two short paragraphs explaining what the next task should give. |

## Continuity recipient selector

Add a contract/schema that lets the Owner select continuity for:

- Prime
- Inquisitor
- Speculum

The selected role must not change project truth. It changes only the role pack, review posture, response contract, and required first-read behavior.

## Required final answer

Use the strict 4-part Owner final answer:

1. Step name.
2. Step verdict.
3. Commit links with short labels.
4. Exactly 3-4 short Russian Owner-facing lines.

All detailed evidence must be in repo artifacts and output bundle, not chat.

## Git closure

If not BLOCK, commit and push are mandatory unless unsafe or explicitly forbidden by Owner.
