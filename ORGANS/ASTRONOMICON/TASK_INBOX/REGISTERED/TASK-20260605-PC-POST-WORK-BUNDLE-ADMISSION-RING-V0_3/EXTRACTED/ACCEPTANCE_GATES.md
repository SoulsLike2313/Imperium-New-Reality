# ACCEPTANCE_GATES.md

## Hard acceptance gates

GATE-01 Task registration
- Registered Astronomicon task is used.
- Current expected task is read or resolved.
- Task ID matches this taskpack.

GATE-02 Officio role and language
- OFFICIO_AGENTIS role entry receipt exists before mutation.
- Owner-facing live/final response after role entry is Russian.
- Machine artifacts are ENGLISH UTF8 NO_BOM.

GATE-03 Standard closure route
- A V0.3 standard task closure contract exists.
- A runnable standard closure command or script exists.
- The command path and replay command are written in final report.

GATE-04 Schema-backed bundle validation
- Common 9-organ receipt schema exists or is strengthened.
- Bundle manifest schema exists or is strengthened.
- Bundle index card schema exists or is strengthened.
- Repair request schema exists or is strengthened.
- Production checker validates at least one positive fixture.

GATE-05 Negative fixtures
At minimum these cases must be represented and checked:
- missing required organ receipt blocks
- malformed organ receipt blocks
- Inquisition BLOCK creates repair request
- missing remote proof blocks accepted closure
- heavy artifact in Git index is warned or blocked by policy

GATE-06 Repair loop
- Administratum must produce repair request on BLOCK.
- Administratum must not produce accepted closure on BLOCK.
- Repair request includes actionable target, owner organ, evidence, and expected fix.

GATE-07 9 organs
The post-work ring must require:
- ASTRONOMICON
- OFFICIO_AGENTIS
- ADMINISTRATUM
- MECHANICUS
- DOCTRINARIUM
- INQUISITION
- STRATEGIUM
- SCHOLA_IMPERIALIS
- CUSTODES

GATE-08 Custodes boundary
- Custodes may audit organ matrix/receipt quality.
- Custodes must not claim full Throne authority.
- Custodes must not claim full semantic truth.

GATE-09 Inquisition contradiction scan
- Inquisition receipt exists.
- Fake green and contradiction boundaries are explicit.
- PASS_WITH_WARNINGS must not be summarized as clean PASS.

GATE-10 Schola Enhanced Ghost Evolve
- SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT exists.
- Mode must be ULTIMATE_ORGAN_TEACHING.
- Lessons must be placed into contracts/schemas/templates/validators/fixtures/read-first/next-route, not only summary.

GATE-11 Git closure
- Commit performed.
- Push performed.
- git status --porcelain=v1 is empty after completion.
- local HEAD equals origin/master.
- Post-push no-write proof is provided without self-reference fake green.

GATE-12 Report bundle
- Final owner summary RU exists.
- Bundle index card exists.
- Receipt index exists.
- File delta index exists.
- Checker report exists.
- Next task route exists.

## Blocking conditions

Block final acceptance if any condition is true:

- no OFFICIO role entry receipt
- owner-facing final answer not Russian
- missing 9-organ ring receipt
- missing Administratum bundle checker report
- checker reports BLOCK
- required schema files are malformed
- no repair request for a known BLOCK fixture
- no git commit/push proof
- no remote equality proof
- full semantic truth is claimed
- full Custodes/Throne authority is claimed
- WARP readiness is claimed
- heavy/private local artifact is committed without explicit admission
