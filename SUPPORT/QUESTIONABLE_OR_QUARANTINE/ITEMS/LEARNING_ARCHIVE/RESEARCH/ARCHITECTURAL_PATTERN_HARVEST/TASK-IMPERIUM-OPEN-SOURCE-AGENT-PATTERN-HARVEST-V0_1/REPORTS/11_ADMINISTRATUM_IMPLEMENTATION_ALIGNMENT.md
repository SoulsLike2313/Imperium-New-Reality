# Administratum-Agent V1 Implementation Alignment

This file maps the harvest into the already committed Administratum-Agent V1 target form.

## Required influence on Administratum V1

| Harvest pattern | Required Administratum behavior |
|---|---|
| MCP boundary | All scripts become Skill Bundles, not loose scripts |
| LangGraph checkpointing | Inventory/classification/summary route writes checkpoint cards |
| Claude subagent frontmatter | Manifest, role contract, explicit tools, memory scope |
| Claude hooks | Agent start/stop and skill start/stop events in ledger |
| SWE-agent ACI | Narrow CLI commands, action parser, output budget |
| SWE trajectories | Run trace JSONL and compact Owner summary |
| OpenHands workspace | Allowed/denied path model; no direct canon mutation |
| MetaGPT SOP | Administratum outputs artifacts for downstream organs |
| CrewAI flows/crews | Sanctum/route controls sequence; agents do bounded work |
| AutoGen typed async | Typed envelopes and route/session IDs |
| AutoGen concurrency warning | Single-writer state; no unsafe parallel stateful calls |
| CLI visual comfort | Color/panel/table presentation, with JSON truth underneath |

## Administratum V1 minimum contracts

1. `AGENT_MANIFEST.json`
2. `ROLE_CONTRACT.md`
3. `POLICIES/`
4. `BRAIN_NODE/rules/`
5. `SKILLS/` with skill bundle manifests
6. `RUNS/` runtime layer
7. `STATE/current_status.json`
8. `RECEIPTS/`
9. `REPORTS/`
10. `TOOLS/administratum_agent_runner.py`

## Do not do

- Do not install external frameworks.
- Do not mutate canon directly.
- Do not make runtime files tracked architecture.
- Do not use pretty CLI as proof.
- Do not run parallel stateful agents by default.
