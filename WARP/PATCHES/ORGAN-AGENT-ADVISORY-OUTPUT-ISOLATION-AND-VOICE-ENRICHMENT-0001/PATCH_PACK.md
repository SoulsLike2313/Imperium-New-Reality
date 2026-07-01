# PATCH PACK — ORGAN-AGENT-ADVISORY-OUTPUT-ISOLATION-AND-VOICE-ENRICHMENT-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON`  
mode: `BUGFIX_AND_VOICE_ENRICHMENT`

## Purpose

Fix advisory output isolation bug and enrich the organ-agent voice.

## Expected verdict

```text
PASS_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_ENRICHED
```

## Expected receipts

```text
ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_output_isolation_voice_receipt.json
```

## What changes

```text
imperium advise
  keeps global summary with all 10 organs

imperium advise organ INQUISITION
  writes isolated per-organ files
  does not overwrite global summary
```

## Next after this

Red + Blue team tools and skills foundation.
