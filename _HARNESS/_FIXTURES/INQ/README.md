# INQ Fixtures Pyramid (v0_1)

20 fixtures organised as:

```
base/      4 fixtures (FX-001 .. FX-004)  -- one positive baseline per detector category
per_tool/  10 fixtures (FX-005 .. FX-014) -- 1-2 per detector, deep into expected verdicts
edge/      6 fixtures (FX-015 .. FX-020)  -- combos, boundaries, unicode, jsonl, deep nesting, unknown submitter
```

## Meta block

Each fixture file has a top-level `_inq_fixture` object:

```json
{
  "_inq_fixture": {
    "id": "FX-005",
    "name": "secrets_openai_key",
    "category": "per_tool",
    "tool": "inq_secrets",
    "expected_verdict": "BLOCK_SECRETS",
    "expected_findings_min": 1,
    "expected_finding_kinds": ["OPENAI_API_KEY"],
    "tags": ["per_tool", "secret", "openai", "block"]
  }
}
```

For PI fixtures where the verdict differs by author class, the meta carries
`expected_verdict_llm` and `expected_verdict_owner`. For the demo-whitelist edge
fixture (FX-015), the meta carries `expected_verdict_with_demo_combo` and
`expected_verdict_without_combo`.

## Golden snapshots

`../INQ_GOLDENS/goldens.json` holds the canonical per-fixture verdict subset
that the test harness compares to live tool output (volatile fields like
`issued_utc` are stripped before comparison).

Regenerate goldens with:

```
python3 ORGANS/INQUISITION/TESTS/update_goldens.py
```

(Once `update_goldens.py` is delivered in the TESTS pack; v0_1 ships goldens
as hand-written canon, with the live snapshot generator scheduled for v0_2.)

## Demo-secrets policy

Fixtures under `_HARNESS/_FIXTURES/INQ/` are tagged for the combo demo
whitelist (Q9): when `TASK_MANIFEST.json` declares `demo_secrets_allowed: true`
AND the matching file path lives under this directory, `inq_secrets` and
`inq_pi_scan` return OK on these fixtures. Without the manifest flag, they
BLOCK as usual.

## Test matrix coverage (T1-T10)

- T1  health smoke              -> inquisition.py --health
- T2  OpenAI secret             -> FX-005
- T3  AWS compound secret       -> FX-006
- T4  entropy-only token        -> FX-007
- T5  PI ignore-previous EN     -> FX-003
- T6  trust update OK delta     -> live (no fixture; uses authors.json round-trip)
- T7  ban auto-trigger          -> live (3 consec BLOCK appends via inq_ban --update)
- T8  redact key=password       -> FX-010
- T9  audit chain immutable     -> FX-014 + 2 appends + verify
- T10 ForceInq override logged  -> FX-005 + --force-inq + audit chain link
