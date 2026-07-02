# PATCH PACK — CUSTODES-ASTRONOMICON-VALIDATION-INVOKE-CONTRACT-FIX-0001

status: `WARP_CANDIDATE`  
owner: `CUSTODES`  
mode: `PROSECUTOR_INVOKE_CONTRACT_FIX`

## Purpose

Fix Custodes false indictment caused by validator invocation contract mismatch.

Custodes remains a strict prosecutor. This patch does not weaken prosecution.

It makes prosecution more correct:

```text
wrong CLI invocation != organ lie
all compatible invocation attempts fail == valid indictment
```

## Expected verdict

```text
PASS_CUSTODES_ASTRONOMICON_VALIDATION_READY
```

## Expected receipt

```text
ORGANS/CUSTODES/RECEIPTS/custodes_astronomicon_validation_receipt.json
```

## Not claimed

```text
Throne verdict
organ assembled
validator infallibility
```
