# CLAIM_LEDGER_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Inquisition`
Support organs: Administratum, Mechanicus, Officio Agentis

## Purpose

Requires every important claim to be traceable: claim -> owner organ -> capability class -> evidence level -> cap -> red-team verdict -> final score.

## Required questions

- What exact claim is made?
- Which organ owns it?
- What evidence level proves it?
- What cap applies?
- Did red-team attack it?

## PASS criteria

- All major claims have ledger entries
- Evidence level and cap are explicit
- Red-team verdict present

## WARN criteria

- Minor claim missing but not used for PASS
- Owner unknown but declared UNKNOWN

## BLOCK criteria

- PASS claim without ledger
- Runtime claim without replay
- Final score ignores cap

## Fake-green flags

- `PASS_WITHOUT_CLAIM_LEDGER`
- `CAP_IGNORED`
- `RUNTIME_CLAIM_NO_REPLAY`

## Evidence requirements

- `CLAIM_LEDGER.jsonl`
- `RED_TEAM_VERDICT.json`
- `EVIDENCE_LEDGER.jsonl`
