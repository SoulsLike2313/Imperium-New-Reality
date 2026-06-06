# Source Index

## SRC-MCP-SPEC-2025-06-18

- System: Model Context Protocol
- Official: True
- Title: Model Context Protocol Specification 2025-06-18
- URL: https://modelcontextprotocol.io/specification/2025-06-18
- Facts:
  - MCP is an open protocol for integrating LLM applications with external data sources and tools.
  - MCP standardizes sharing context, exposing tools/capabilities, and building composable integrations/workflows.
  - MCP uses JSON-RPC 2.0 messages between hosts, clients, and servers.
- IMPERIUM takeaway: Translate MCP into a sovereign Skill Bundle Protocol and Tool State Protocol; do not install or adopt MCP as a master architecture.


## SRC-LANGGRAPH-PERSISTENCE

- System: LangGraph
- Official: True
- Title: LangGraph Persistence
- URL: https://docs.langchain.com/oss/python/langgraph/persistence
- Facts:
  - LangGraph persistence saves graph state as checkpoints at every step when compiled with a checkpointer.
  - Checkpoints enable human-in-the-loop inspection/approval, memory, time travel debugging, and fault-tolerant execution.
  - Graph executions are organized into threads.
- IMPERIUM takeaway: Translate to Route/Checkpoint Protocol with resumable run state, Owner approval points, time-travel/debug snapshots, and fault recovery.


## SRC-CLAUDE-CODE-SUBAGENTS

- System: Claude Code subagents
- Official: True
- Title: Create custom subagents - Claude Code Docs
- URL: https://code.claude.com/docs/en/sub-agents
- Facts:
  - Subagents are defined in Markdown files with YAML frontmatter.
  - Subagents can be user-level, project-level, managed settings, CLI-session, or plugin-provided.
  - A subagent can be configured with tool access, model choice, color, and persistent memory.
- IMPERIUM takeaway: Translate to Organ-Agent manifest + role contract + tool admission + visual CLI identity + memory scope.


## SRC-CLAUDE-CODE-HOOKS

- System: Claude Code hooks
- Official: True
- Title: Claude Code Hooks Reference
- URL: https://code.claude.com/docs/en/hooks
- Facts:
  - Hooks can run when subagents start or stop.
  - SubagentStart receives agent_id and agent_type and can inject additional context.
  - SubagentStop receives subagent transcript path and last assistant message.
- IMPERIUM takeaway: Translate to Agent Event Hooks and Receipts: start/stop events, transcript paths, injected context, and run ledger.


## SRC-SWE-AGENT-ARCHITECTURE

- System: SWE-agent
- Official: True
- Title: SWE-agent Architecture
- URL: https://swe-agent.com/latest/background/architecture/
- Facts:
  - SWE-agent central entry point is a CLI executable.
  - It initializes an environment, shell session, custom tools/ACI, configurable agent, history processor, action parser, and execution loop.
  - SWE-agent documentation notes it has been superseded by mini-swe-agent and is now maintenance-only.
- IMPERIUM takeaway: Translate to clean CLI runner, sandboxed execution surface, action parser, history compressor, and tool bundle interface; avoid adopting an obsolete framework.


## SRC-SWE-AGENT-ACI

- System: SWE-agent ACI
- Official: True
- Title: Agent-Computer Interface
- URL: https://github.com/SWE-agent/SWE-agent/blob/main/docs/background/aci.md
- Facts:
  - SWE-agent centers the idea of an Agent-Computer Interface: tools and interaction format enabling an agent to interact with a computer environment.
  - ACI design materially affects agent behavior and performance.
- IMPERIUM takeaway: Translate to IMPERIUM Agent-Computer Interface: narrow command grammar, receipts, safe shell exposure, and script-first capabilities.


## SRC-SWE-AGENT-TRAJECTORIES

- System: SWE-agent trajectories
- Official: True
- Title: SWE-agent trajectories
- URL: https://swe-agent.com/latest/usage/inspector/
- Facts:
  - Trajectories are SWE-agent's main output for understanding what the agent does.
  - SWE-agent provides CLI and web inspectors for trajectory files.
- IMPERIUM takeaway: Translate to Route Session Trajectory + Inspector-ready receipts, not only final answers.


## SRC-OPENHANDS-SITE

- System: OpenHands
- Official: True
- Title: OpenHands official site
- URL: https://www.openhands.dev/
- Facts:
  - OpenHands is an AI agent platform for software development that can plan, write, apply changes, and complete engineering tasks end-to-end.
  - OpenHands emphasizes large/legacy codebase handling, dependency mapping, and safe parallel agent work.
- IMPERIUM takeaway: Translate to Workspace Boundary, large-repo map, controlled parallelism, and end-to-end task proof; do not hand control to external agent platform.


## SRC-OPENHANDS-PAPER

- System: OpenHands paper
- Official: False
- Title: OpenHands: An Open Platform for AI Software Developers
- URL: https://arxiv.org/abs/2407.16741
- Facts:
  - The OpenHands paper describes agents interacting through code writing, command line, and web browsing.
  - It highlights sandboxed environments for code execution, multi-agent coordination, and evaluation benchmarks.
- IMPERIUM takeaway: Translate to sandboxed workspaces, action channels, benchmark/eval suites, and browser/tool boundaries.


## SRC-METAGPT-DOCS

- System: MetaGPT
- Official: True
- Title: MetaGPT introduction
- URL: https://docs.deepwisdom.ai/main/en/guide/get_started/introduction.html
- Facts:
  - MetaGPT takes a one-line requirement and outputs artifacts such as user stories, competitive analysis, requirements, data structures, APIs, and documents.
  - MetaGPT models a software company using roles like product managers, architects, project managers, and engineers.
  - Its stated philosophy is Code = SOP(Team): materialized SOP applied to LLM teams.
- IMPERIUM takeaway: Translate to Organ SOP pipeline and artifact chain; accept structured role workflows, reject theatrical roleplay and uncontrolled cascade.


## SRC-CREWAI-DOCS

- System: CrewAI
- Official: True
- Title: CrewAI Documentation
- URL: https://docs.crewai.com/
- Facts:
  - CrewAI describes collaborative agents, crews, and flows.
  - It emphasizes guardrails, memory, knowledge, observability, and structured outputs.
- IMPERIUM takeaway: Translate to controlled teams, observability, flow-managed state, and typed outputs; do not import CrewAI as host.


## SRC-CREWAI-INTRO

- System: CrewAI
- Official: True
- Title: CrewAI Introduction
- URL: https://docs.crewai.com/en/introduction
- Facts:
  - CrewAI Flows manage state and control execution.
  - Crews are teams of autonomous agents delegated tasks by Flows.
  - Flows provide state management, event-driven execution, control flow, conditional logic, loops, and branching.
- IMPERIUM takeaway: Translate to Sanctum/Route manager as flow controller and Organ-Agent groups as crews, but keep deterministic gates and local sovereignty.


## SRC-AUTOGEN-MS-RESEARCH

- System: AutoGen
- Official: True
- Title: AutoGen - Microsoft Research
- URL: https://www.microsoft.com/en-us/research/project/autogen/
- Facts:
  - AutoGen is an open-source framework for building AI agents and facilitating cooperation among multiple agents.
  - AutoGen v0.4 emphasizes asynchronous messaging, modular extensibility, observability/debugging, scalable/distributed networks, extensions, cross-language support, and type support.
- IMPERIUM takeaway: Translate to typed async event bus, modular tool/agent interfaces, tracing, and cross-language adapter boundaries.


## SRC-AUTOGEN-AGENTS

- System: AutoGen agentchat
- Official: True
- Title: AutoGen Agents tutorial
- URL: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html
- Facts:
  - AutoGen supports using an agent as a tool.
  - It warns to disable parallel tool calls when tools or agent teams have internal state that can conflict.
  - Structured output can be validated with schema-like Python models.
- IMPERIUM takeaway: Translate to Agent-as-tool admission, side-effect concurrency lock, max iteration budgets, and typed output contracts.
