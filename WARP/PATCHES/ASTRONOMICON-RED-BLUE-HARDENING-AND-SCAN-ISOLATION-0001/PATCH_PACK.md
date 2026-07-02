# PATCH PACK — ASTRONOMICON-RED-BLUE-HARDENING-AND-SCAN-ISOLATION-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + INQUISITION`  
mode: `ORGAN_LOCAL_RED_BLUE_HARDENING`

## Purpose

Harden Astronomicon Red/Blue locally before Custodes audit and Throne strict gates.

Also fix the Red/Blue scan output isolation bug.

## Expected verdict

```text
PASS_ASTRONOMICON_RED_BLUE_HARDENED_AND_SCAN_ISOLATED
```

## Expected scores

```text
red_local_hardening_score >= 80
blue_local_hardening_score >= 80
red_team_proven_score = 0
blue_team_proven_score = 0
custodes_validation_score = 0
throne_confirmation_score = 0
```

## Expected receipts

```text
ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_red_blue_hardening_receipt.json
ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_red_blue_hardening_scan_isolation_receipt.json
```

## Next

```text
CUSTODES-ASTRONOMICON-VALIDATION-0001
THRONE-ASTRONOMICON-STRICT-GATES-0001
POST-ASTRONOMICON-SCORE-READOUT-0001
```
