# Execution Protocol — TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5

## Step A — Read and acknowledge

Read all taskpack files. Produce internal ACK:
- scope is New Generation only;
- wrong ORGANS/MECHANICUS report root was an error;
- no VM2;
- Mechanicus click panel is mandatory.

## Step B — Git truth

Run:
```powershell
cd E:\IMPERIUM
git rev-parse HEAD
git status --short
git log -1 --oneline
```

Record into:
`IMPERIUM_NEW_GENERATION\REPORTS\TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5\git_start_truth.txt`

## Step C — Scope audit

Run or implement a lightweight scope scanner:
- list changed files
- list untracked files
- classify forbidden-path writes
- detect previous V0_3/V0_4 wrong reports under `ORGANS/`

Report to:
- `scope_contamination_audit.md/json`
- `git_diff_scope_report.json`

## Step D — Repair forbidden artifacts

If wrong-scope task artifacts are uncommitted:
- copy diagnostic evidence to New Generation report folder if useful;
- remove/restore wrong-scope uncommitted files;
- record all actions.

If committed:
- do not rewrite history;
- create a safe corrective commit only for task-owned artifacts, or mark WARN/BLOCK with Owner decision options.

## Step E — Implement UI repair under New Generation

Work only in:
`IMPERIUM_NEW_GENERATION/**`

Expected likely roots:
- `IMPERIUM_NEW_GENERATION/SANCTUM_MINI/**`
- `IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/MECHANICUS_AGENT/**`
- `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5/**`

## Step F — Test interaction

Use Playwright or equivalent:
- open Sanctum
- verify overview visible
- click Mechanicus
- assert panel opens
- assert selected state visible
- run status/tools
- verify panel updates
- verify raw mode is separate

## Step G — Test responsive layout

Capture:
- 1366x768
- 1920x1080

Check:
- horizontal page overflow
- hidden controls
- readable text
- primary panel not raw terminal dump

## Step H — Test SSE/live truth

If EventSource connects:
- prove heartbeat
- prove state snapshot
- prove command event
- screenshot UI `SSE CONNECTED`

If fallback:
- UI and reports must say `SSE FALLBACK`
- verdict cannot say `SSE TESTED PASS`

## Step I — Validate

Run available checks:
- Python compile touched Python
- node/js syntax
- JSON validation
- API health/state/actions
- Playwright interaction proof
- scope lock check

## Step J — Commit

Only commit if no BLOCK:
```powershell
git status --short
git diff --name-only
```

Ensure changed paths are under `IMPERIUM_NEW_GENERATION/**`.

Commit message suggestion:
`TASK-20260520: repair New Generation Sanctum Mechanicus panel scope and UX`

Push and record:
- HEAD
- status
- GitHub link

## Final response

Use `08_FINAL_REPORT_TEMPLATE_RU.md`.
