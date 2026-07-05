# PATCH PACK — MECHANICUS-JSON-EVIDENCE-STRICT-LANE-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + CUSTODES + THRONE`  
mode: `JSON_EVIDENCE_STRICT_LANE`

## Purpose

Resolve current `json_evidence` debt without fake green.

Observed debt:

```text
2 malformed fixture JSON files
1 quarantine JSONL with extra data
```

This patch classifies them instead of blindly repairing them.

## Boundary

```text
Parse clean is not schema truth.
Schema truth is not semantic truth.
Semantic truth is not organ honesty.
```
