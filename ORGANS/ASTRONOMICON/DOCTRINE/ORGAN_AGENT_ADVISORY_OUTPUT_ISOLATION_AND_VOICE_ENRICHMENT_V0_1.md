# ORGAN AGENT ADVISORY OUTPUT ISOLATION AND VOICE ENRICHMENT V0.1

patch_id: `ORGAN-AGENT-ADVISORY-OUTPUT-ISOLATION-AND-VOICE-ENRICHMENT-0001`

## Purpose

Close the advisory output bug.

Single-organ advisory calls must not overwrite the global advisory summary.

## Correct output law

```text
imperium advise
  -> ORGAN_AGENT_ADVISORY_SUMMARY_V0_1.json
  -> ORGAN_AGENT_ADVISORY_REPORT_V0_1.md

imperium advise organ INQUISITION
  -> ORGAN_AGENT_ADVISORY_INQUISITION_V0_1.json
  -> ORGAN_AGENT_ADVISORY_INQUISITION_V0_1.md
```

## Voice enrichment

The organ-agent should be helpful and talkative, but still bounded.

Every advisory item must include:

```text
what is visible
why this zone matters
what raises future-step success probability
what reduces future-step success probability
evidence considered
what is not claimed
```

## Boundary

The organ-agent recommends attention zones. It does not command concrete actions, claim trust, or claim Throne verdict.
