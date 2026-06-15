# Agent Summary EN — Architectural Pattern Harvest

## Status

This is an advisory research pack for IMPERIUM New Generation. It introduces no OSS dependencies and performs no implementation.

## Objective

Extract architectural patterns from external agent/tool systems and translate them into IMPERIUM-native contracts for future Organ-Agent implementation, especially `ADMINISTRATUM_AGENT` V1.

## Reference systems

- Model Context Protocol (MCP)
- LangGraph
- Claude Code subagents and hooks
- SWE-agent / mini-swe-agent concepts
- OpenHands
- MetaGPT
- CrewAI
- AutoGen

## Non-adoption rule

External systems are references only. Do not install, import, or make them the host architecture.

## Core translations

| External pattern | IMPERIUM-native translation |
|---|---|
| MCP host/client/server and tools/resources/prompts | Skill Bundle Protocol + Tool State Protocol |
| LangGraph checkpointed state | Route/Checkpoint Protocol |
| Claude Code subagent definitions | Organ-Agent Manifest + Role Contract |
| Claude hooks | Agent Event Ledger + Lifecycle Receipts |
| SWE-agent ACI | IMPERIUM Agent-Computer Interface |
| SWE-agent trajectories | Route Session Trajectory + trace inspector |
| OpenHands sandbox/workspace | Workspace Permission Boundary |
| MetaGPT SOP/team pipeline | Organ SOP Pipeline |
| CrewAI flows/crews | Sanctum Route Manager + Controlled Organ Groups |
| AutoGen async typed agents | Organ Event Bus + Typed Message Protocol |
| AutoGen agent-as-tool warnings | Side-effect lock + concurrency admission |
| Owner CLI comfort requirement | CLI Visual Comfort Contract |

## Implementation constraints

1. No external dependency introduced by this pack.
2. No canon mutation by Organ-Agents.
3. Runtime outputs must go to `RUNS/` or another ignored runtime layer.
4. Every route step needs checkpoint/receipt.
5. Every tool/skill needs manifest, input/output schema, side-effect policy, and verification.
6. Agent messages need typed envelopes and route/session IDs.
7. CLI UI is presentation only; machine truth remains JSON/JSONL/receipts.
8. No green status without verification.
