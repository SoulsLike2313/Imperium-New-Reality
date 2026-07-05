# PATCH PACK — MECHANICUS-TOOL-ACCUMULATION-AND-ADMISSION-GATE-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + CUSTODES + THRONE`  
mode: `TOOL_ACCUMULATION_AND_ADMISSION_GATE`

## Purpose

Record Owner intent: Mechanicus accumulates and governs tools.

Mechanicus does not need to personally author every tool. It must know, classify, admit, reject and track:

- external tools: languages, libraries, engines, compilers, package managers, linters, formatters, build systems;
- internal tools: validators, scanners, runners, adapters, UI helpers, Codex/Grok/Logos-created task tools.

## Executor loop

If Codex/Grok/Servitor creates a tool during a task and Mechanicus rejects it, the task should not silently stop. The executor must fix the tool inside the task loop until it passes admission or an Owner-visible blocker is declared.

## Boundary

This patch creates admission law and inventory baseline. It does not claim strict cleanliness for every tool.
