# ACCEPTANCE GATES

## Gate 1: Owner Audit Card contract

PASS requires a committed contract for the Owner Audit Card review format.

The contract must define:

- trigger condition;
- section order;
- quick verdict table;
- accepted evidence table;
- concerns/risk table;
- short conclusion;
- exactly two short paragraphs for next task value;
- no long chat report unless Owner asks.

## Gate 2: Continuity recipient selector

PASS requires a schema or contract for choosing continuity recipient target:

- LOGOS_PRIME;
- INQUISITOR;
- SPECULUM.

Core continuity truth must be role-neutral. Role pack must be separate.

## Gate 3: Role pack bridge

PASS requires role-pack bridge definition that maps:

- recipient target;
- role owner organ;
- first-read files;
- response mode;
- review posture;
- cleanliness checks.

## Gate 4: Clean context guard

PASS requires Inquisition-facing guard notes or receipt proving:

- no fake continuity;
- no stale role assumption;
- no private data leakage;
- role pack does not alter core truth;
- clean role and clean answers are expected.

## Gate 5: Mechanicus validation

PASS requires Mechanicus validation receipt or explicit validation-limitation receipt.

Validation should check schema readability, JSON parseability, required files, and UTF-8 safety where applicable.

## Gate 6: Officio response integration

PASS requires Officio response contract linkage. The Owner Audit Card must be registered as a Logos review response format or candidate response format.

## Gate 7: Git closure

PASS_WITH_WARNINGS or PASS requires commit and push unless blocked by unsafe gate or explicit Owner instruction.

Required:

- commit hash;
- push status;
- origin/master == HEAD check;
- clean worktree check;
- commit_push_receipt.json.

## Gate 8: Forbidden expansion

Do not implement:

- full IDE;
- WARP;
- VM2/VM3 live route;
- broad skill-system rewrite;
- private context harvesting.
