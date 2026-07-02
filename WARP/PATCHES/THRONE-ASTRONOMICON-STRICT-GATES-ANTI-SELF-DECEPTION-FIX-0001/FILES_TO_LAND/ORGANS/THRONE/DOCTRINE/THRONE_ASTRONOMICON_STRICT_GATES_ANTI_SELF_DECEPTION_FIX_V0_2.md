# THRONE ASTRONOMICON STRICT GATES — ANTI SELF-DECEPTION FIX V0.2

patch_id: `THRONE-ASTRONOMICON-STRICT-GATES-ANTI-SELF-DECEPTION-FIX-0001`

## Problem

The previous strict gate passed correctly on external evidence, but its language was too easy to read as:

```text
Throne validated itself.
```

That is forbidden.

## Correct law

```text
Custodes = prosecutor.
Throne = Crown order.
Throne validator = local consistency check, not proof that Throne itself is truthful.
```

So we separate fields:

```text
astronomicon_crown_order_score = Crown order over Astronomicon evidence
throne_self_validation_score = proof that Throne itself is valid
```

In this patch:

```text
astronomicon_crown_order_score: may be 100
throne_self_validation_score: must remain 0
astronomicon_assembled_score: must remain 0
```

## Meaning

The Throne can issue a severe local order for Astronomicon, but it must not pretend that its own validator is an external witness for Throne itself.
