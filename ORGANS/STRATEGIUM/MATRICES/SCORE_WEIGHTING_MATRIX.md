# SCORE_WEIGHTING_MATRIX — V0.4 Candidate

Owner organ: `Strategium`
Support organs: `Inquisition, Mechanicus, Administratum`
Status: `CANDIDATE`
Candidate repo location: `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/MATRICES/SCORE_WEIGHTING_MATRIX.md`

## Purpose
Weights readiness dimensions by current campaign priority instead of hiding mixed goals in one number.

## Used by
INQUISITOR, GPT_LOGOS, SERVITOR, SCHOLA

## Required questions
- What is the source of truth for this claim?
- Which organ owns the rule?
- What evidence level proves it?
- What cap applies if evidence is missing?
- What would make this claim fake-green?

## PASS/WARN/BLOCK

### PASS
- All required fields present
- Owner organ declared
- Evidence level E3+ for runtime claims or explicit cap
- Fake-green flags reviewed

### WARN
- Candidate location only
- Evidence below E3 but not claiming runtime
- Owner decision pending

### BLOCK
- Owner unknown
- Capability claimed without evidence
- Contradicts declared HEAD or dirty/provenance state

## Fake-green flags
- `CLAIM_WITHOUT_REPLAY`
- `AGENT_REASONING_AS_SYSTEM_CAPABILITY`
- `STALE_RECEIPT`
- `DIRTY_STATE_HIDDEN`
- `OWNER_DECISION_MISSING`

## Score caps
- If `evidence_level <= E1_FILE_EXISTS` -> cap `35%`
- If `runtime_claim_without_replay` -> cap `40%`
- If `owner_decision_required_but_missing` -> cap `60%`

## Evidence requirements
- E1 minimum for existence
- E3 for executed behavior
- E4 for stable pass
- E5 for audit confidence
- E6 for Owner-facing UX acceptance
