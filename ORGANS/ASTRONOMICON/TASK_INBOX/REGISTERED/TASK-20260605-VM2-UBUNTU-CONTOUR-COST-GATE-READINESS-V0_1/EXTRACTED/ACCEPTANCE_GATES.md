# ACCEPTANCE_GATES

## Admission and role gates

- Astronomicon admission must pass before execution.
- Servitor must enter role through OFFICIO_AGENTIS before mutation.
- Owner-facing final answer must be Russian after OFFICIO role entry.
- Machine artifacts must be ENGLISH UTF8 NO_BOM.

## VM2 readiness gates

- VM2 readiness receipt exists.
- Receipt records OS, hostname, shell, repo root, python, git, local HEAD, remote HEAD, and worktree state.
- Start state proves local HEAD equals origin/master or records a BLOCK/WARN with evidence.
- New Reality root is confirmed.
- Ancient Empire is not used.

## Compatibility gates

- Windows PC to Ubuntu VM2 compatibility receipt exists.
- It covers path separators, SSH route, shell differences, UTF8 NO_BOM, LF/CRLF risk, script executable/shebang risk, and repo root mapping.

## Strategium cost gate gates

- ORGANS/STRATEGIUM/COST_GATE exists.
- Contract, schemas, templates, checker, and fixtures exist.
- Cost checker runs successfully on a positive fixture.
- Cost checker blocks or fails a negative fixture.
- Current task produces STRATEGIUM_TASK_BUDGET_CARD.json, STRATEGIUM_TASK_COST_RECEIPT.json, and STRATEGIUM_KPD_DELTA_RECEIPT.json.
- Unknown token usage is written as UNKNOWN_WITH_REASON, not as a fake number.

## Mechanicus gates

- Any new checker script has a Mechanicus tool card or a precise reason why registration could not be completed.

## Bundle and closure gates

- Report folder exists: REPORTS/TASK-20260605-VM2-UBUNTU-CONTOUR-COST-GATE-READINESS-V0_1/
- Bundle index or Administratum-compatible report index exists.
- If the V0.2 bundle checker is available, it is run.
- If it cannot run, the limitation is recorded as a warning, not a PASS.
- git status is checked before final response.
- Commit and normal non-force push are performed if files changed.
- Final response includes local HEAD, origin/master HEAD, and whether they match.

## Cost discipline gates

- Scope expansion count is recorded.
- Next task budget recommendation is recorded.
- If actual cost exceeds planned budget, overrun reason is recorded.

## No fake green

- No PASS may claim real token counts unless measured.
- No PASS may claim full production closure.
- No PASS may claim WARP readiness.
- No PASS may claim full Custodes or Throne authority.
