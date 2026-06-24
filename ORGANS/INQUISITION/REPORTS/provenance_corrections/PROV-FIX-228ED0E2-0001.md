# PROV-FIX-228ED0E2-0001 — provenance correction

**Target commit:** `228ed0e2` — *"REALITY-HYGIENE-GUARD-0001: route Inquisition negative evidence outside REALITY"*
**Authored externally by:** GPT 5.5
**Landed:** before the INQUISITION land gate became canon (`0cfb1c8b`, 2026-06-24).

## What was claimed
The `TASK_MANIFEST.json` bundled in commit `228ed0e2` declared its base as `8bd511d6` (DOCTR-ANATOMY).

## What was true
The actual `git parent` of `228ed0e2` is `461e23ce` (OWNER-PROFILE-0001).
`8bd511d6` is not the immediate ancestor — it sits one hop further back.

If the gate that lives at `ORGANS/INQUISITION/TOOLS/inq_land_gate_v0_1.py` had existed at land-time, this commit would have been **DENIED** with `G3_PROVENANCE_LIE`.

## Why we are not rewriting history
Public `master` is the canonical reality per WARP_OPERATION_SPINE_V0_5. Rewriting history would break every downstream clone and every future provenance check that anchors on existing SHAs. The canonical remedy is this corrective receipt.

## What this receipt does
- Records the lie in the same organ that would have caught it.
- Marks the `declared_base` field of `228ed0e2`'s in-commit manifest as **FORGED** for all future audits.
- Closes the open provenance debt that was carried since this session's discovery.

## What it does NOT do
- It does not invalidate the *content* of `228ed0e2` (the hygiene-guard logic). That content stands on its own merit and was already integrated.
- It does not penalize the owner. The land happened during the pre-gate era; the discipline gap has since been closed by `KERNEL-GATE-HARDENING-0001` (`0cfb1c8b`).

## Issuance
- Issued by: **NOTION_OPUS**
- Session: this thread
- Master tip at issuance: `8c8db6c` (INQ-GATE-BOM-TOLERANT-0001)
