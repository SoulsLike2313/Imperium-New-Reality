# Negative Test / Mutation Check V0.1 (Foundation)

## Purpose
Establish a safe synthetic negative-test foundation that proves NewGen can reject known-bad mutant patterns and prevent fake-green promotion.

## Scope
- Synthetic mutants only.
- No production artifact mutation.
- No destructive runtime mutation testing.

## Required Checks
- Known-bad mutants are classified as `BLOCK`, `WARN`, or `REJECTED`.
- No known-bad mutant may be classified `PASS_STRICT`.
- Fake-green attempts are rejected by rule.
- Private-key handling uses synthetic marker only, never real key material.

## Claim Boundary
Allowed claim: `NEGATIVE_TEST_MUTATION_CHECK_FOUNDATION`.
Forbidden claim: production destructive testing readiness.
