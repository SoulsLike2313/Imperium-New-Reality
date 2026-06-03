# Hard Red-Team Closure Gate

Status: `CANDIDATE_V0_1`

No substantial task may close as PASS until it has attacked its own claims.

Required checks:

- HEAD/status/evidence boundary match;
- dirty/provenance contradiction;
- stale receipt;
- role/authority not read;
- manual reasoning claimed as capability;
- screenshot without semantic truth;
- missing replay command;
- commit/push policy compliance;
- output format mismatch;
- private/local leak risk.

Output: `RED_TEAM_VERDICT.json` must be created or the final verdict is capped at WARN.

Commit/push policy compliance rule:

- if substantial task residue exists and commit/push was skipped without explicit `BLOCK_OWNER_INPUT_REQUIRED_TO_CONTINUE`, trigger hard downgrade (`CAP_COMMIT_PUSH_POLICY_VIOLATION`);
- if skip reason is owner-input block, verify receipt includes exact `owner_question_or_instruction`; otherwise downgrade as fake-green.
