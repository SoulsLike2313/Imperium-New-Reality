# Real Servitor Roster TUI Guide

Status: CANDIDATE_V0_1

The TUI Agents and Servitors screen uses this primary source:

ORGANS/IMPERIAL_IDE/AGENTS/agent_registry.json

Primary view shows 12 real servitors: PRIME, ASTRONOMICON, MECHANICUS, ADMINISTRATUM, INQUISITION, STRATEGIUM, DOCTRINARIUM, OFFICIO_AGENTIS, SCHOLA_IMPERIALIS, WARP, METAOS, IMPERIAL_IDE.

Each row shows status, owner organ, execution mode, handoff mode, current expected task, allowed actions, and blocked actions.

Legacy Alpha/Beta/Gamma is not the primary roster. If legacy capsule config is needed for debugging, it is debug-only and must not replace the real registry.

Servitor Prime remains EXTERNAL_HANDOFF_ONLY; real execution remains gated.
