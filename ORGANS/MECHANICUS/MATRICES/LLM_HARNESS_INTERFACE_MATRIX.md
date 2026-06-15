# LLM_HARNESS_INTERFACE_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Mechanicus`
Support organs: Officio Agentis, Astronomicon, Inquisition

## Purpose

Defines script-first interface between local tools/organ packets and a large LLM: gather settings, package context, validate output, store receipts.

## Required questions

- What script/tool gathers the focus packet?
- What files are allowed into context?
- What output schema must be returned?
- Which commands verify the result?
- How is leakage/private boundary prevented?

## PASS criteria

- Context packet has manifest
- Output has schema
- Replay command exists or gap declared
- Private boundary is declared

## WARN criteria

- Harness is manual but documented
- Tool is candidate not canon
- Replay missing but no runtime PASS claimed

## BLOCK criteria

- Broad private context included without policy
- No manifest
- No output schema
- Claims replay but no command

## Fake-green flags

- `CONTEXT_DUMP_WITHOUT_MANIFEST`
- `PRIVATE_LEAK_RISK`
- `OUTPUT_UNSCHEMAED`
- `NO_REPLAY`

## Evidence requirements

- `context_manifest`
- `tool_card`
- `replay_command`
- `validation_receipt`
