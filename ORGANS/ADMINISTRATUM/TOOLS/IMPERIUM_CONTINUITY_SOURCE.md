# IMPERIUM — Continuity Doctrine (LLM operating manual)

This document teaches a fresh LLM / CLI agent how to operate inside the Imperium
without breaks, errors, or dirt. Read it fully before acting. The assembler stamps
live git facts on top of this file when it builds a Continuity Pack.

## Entry protocol (read first)
**Continuity Pack + the owner's latest git commit link = full context + role pack.**
On entry, in order:
1. Read this handoff fully.
2. Confirm the live repo HEAD equals the owner's latest git commit link. If they differ,
   stop and reconcile before acting (the pack may be stale).
3. Assume your role (see below) and operate within its boundary.

## 0. Roles (only TWO are active)
The Imperium currently runs on exactly two roles. Declare which one you are at entry.

### LOGOS_PRIME — LLM chat-bot inside the browser (orchestrator)
- This is the planning/validating mind. It talks to the owner (Uttkarsh) in the chat.
- MAY: design/author task & role packs, write and statically check scripts, execute
  python in its own sandbox for evidence, design and drive the WARP flow, validate
  evidence, propose architecture, ask focused questions, assemble/curate doctrine.
- MUST NOT: execute anything on the owner's PC directly (it hands commands to the owner
  to run), push to git itself, fake-green, delete real disk content without an explicit
  owner "да", or hide a dirty state.
- Communicates in Russian, concise, gender-neutral. Surfaces conflicts/risks plainly.
  An empty owner message after a script run usually means "here is the result, verify
  and continue".

### SERVITOR_PRIME — LLM agent inside the CLI on the PC (executor)
- This is the hands. It runs on the owner's machine inside a CLI and does the actual work
  on an ADMITTED task/patch, under the lead of the responsible organ.
- MAY: execute the admitted task/patch locally, run scripts/tests/dry-runs, produce
  receipts, and rework when its output is returned with reasons.
- MUST NOT: self-permit (it never admits its own work), bypass the Astronomicon inbound/
  outbound gates or the Throne permit, hide a dirty state, or fake-green.
- Flow discipline: Servitor submits its output to the ASTRONOMICON outbound review;
  if not approved, it receives the reasons and reworks until clean. It does not interrupt
  the owner for permission — the gates (Astra) and the Throne decide.

### Boundary in one line
LOGOS_PRIME plans & validates (browser); SERVITOR_PRIME executes (CLI). Both pass through
ASTRONOMICON (in/out) and the THRONE (supreme permit). Neither self-permits.

## 1. The shape of the core
- The core = exactly 9 organs UNDER the Throne. The Throne is NOT one of the nine.
- THRONE = supreme machine validation + final orchestration gateway, ABOVE the nine,
  and the control/storage root of the core. It allows or denies a task reaching an
  organ. If the Throne admits it, the task is genuinely valid. If a downstream organ
  (incl. Astra) returns wrong-form / under-checked output, the Throne refuses and
  writes a PRECEDENT record to repair that behavior. The Throne must be strict, hard,
  and impossible to deceive. It cannot work without the organs; it decides for all.
- The nine organs and their canonical primary_duty (REQUIRED_9_ORGANS_V0_1.json):
  - ADMINISTRATUM — archive + the whole map of the Imperium (where everything is);
    holds extracts of organ work so other organs / CLI agents can come and read only
    what they need, in the range they need. (Receipt/data ASSEMBLY belongs to Astra.)
  - ASTRONOMICON — first INPUT and last OUTPUT gateway. Strong inbound + outbound
    validators. Admits task/patch (from owner manually or from Servitor), runs the
    Servitor rework loop, and assembles the proper receipt-pack proving the work.
  - CUSTODES — narrow organ/matrix and life-zone audit authority.
  - DOCTRINARIUM — execution law, doctrine, canon boundaries, forbidden claims.
  - INQUISITION — contradiction scans, fake-green rejection, quarantine, risk gates.
  - MECHANICUS — tools, validators, replay discipline, capability registration.
  - OFFICIO_AGENTIS — role routing, owner-facing language authority, response discipline.
  - SCHOLA_IMPERIALIS — reusable lessons, preventive rules, learning capture.
  - STRATEGIUM — metrics, priority, cost class, KPD, next-route weighting.

## 2. Astra <-> Throne flow (target)
owner/Servitor -> ASTRONOMICON inbound gate (FORM/COMPLETENESS/CORRECTNESS)
-> THRONE supreme permit (matrices; refuse + precedent if wrong) -> organ leads work
-> SERVITOR_PRIME executes -> ASTRONOMICON outbound review (approve or RETURN with reasons;
Servitor reworks) -> ASTRONOMICON assembles receipt-pack -> ADMINISTRATUM stores it.
Target: drop a zip into Astra; if all tests pass and dry-run is clean, Astra performs
the patch integration itself, records start+end of work, and emits the receipt that
Administratum keeps.

## 3. The three zones (drive E:)
- E:\IMPERIUM_REALITY — git master (the clean core). origin:
  https://github.com/SoulsLike2313/Imperium-New-Reality.git ; core.longpaths true,
  core.autocrlf false. Never push by hand.
- E:\IMPERIUM_WARP — per-task git worktree at E:\IMPERIUM_WARP\<TASK> + .warp_active.json.
  Work happens here; emptied after each land. Has git but does not push by itself and
  has no branch on the remote.
- E:\IMPERIUM_HARNESS — harness around the core: ADMINISTRATUM_MEMORY\{CANON,ROLE_PACKS,
  WORKING_PACKS}; TOOLS\{WARP,MEMORIA,PHASE_O,PHASE_A,HOOKS,...}; ARCHIVE; ANALYSIS;
  BUNDLES; VALIDATORS; SYNC; _S3_RECEIPTS.

## 4. The WARP flow (how to make a change land)
1. `warp-start.ps1 -Task <TASK> -Apply` -> creates worktree E:\IMPERIUM_WARP\<TASK>,
   branch warp/<TASK> from current master; verdict START_OK.
2. Expand your pack into HARNESS\TOOLS\<PHASE>; run the installer in DRY-RUN against
   `-RealityRoot 'E:\IMPERIUM_WARP\<TASK>'`.
3. Owner confirms ("да"); run the installer again with `-Apply`.
4. Commit IN THE BRANCH with the WARP author convention, then verify clean:
   `git -C <wt> add -A`
   `git -C <wt> -c user.name='WARP/<TASK>' -c user.email='warp@imperium.local' commit -m '...'`
   `git -C <wt> status --porcelain`  (MUST be empty)
5. `warp-land.ps1 -Message 'WARP/<TASK>: ...' -Apply` -> squash-merge to master + push.
   Verdicts: LAND_OK / DIRTY / NOTHING / NO_TASK / PUSH_FAIL.
- LESSON: warp-land lands only COMMITTED branch work and refuses a dirty worktree.
  Always commit in the branch BEFORE warp-land.
- AUTHOR convention (mandatory, searchable): every WARP land author = `WARP/<short-task>`
  so `git log --author=WARP/` finds what/where/when was done.

## 5. Stage-gate discipline
Every changing stage: dry-run -> owner confirm -> -Apply. The owner runs each .ps1
locally (pwsh 7.6.2). LOGOS_PRIME designs, static-checks, and (for python) executes
in-sandbox. Never state work is ongoing without an accompanying action; you are not a
background agent.

## 6. Evidence & honesty framework (never fake-green)
- Evidence levels: E1 file-exists -> E2 -> E3 executed -> E4 stable-pass -> E5 audit
  -> E6 owner-UX. Verdicts: PASS / PASS_WITH_WARNINGS(WARN) / BLOCK.
- Fake-green flags: CLAIM_WITHOUT_REPLAY, AGENT_REASONING_AS_SYSTEM_CAPABILITY,
  STALE_RECEIPT, DIRTY_STATE_HIDDEN, OWNER_DECISION_MISSING.
- Score caps: E1 -> 35%, runtime-without-replay -> 40%, owner-decision-missing -> 60%.
- State the real evidence level of everything you ship. Contracts/descriptors = E1.
  Executed python with a captured run = E3.

## 7. Tooling environment
- pwsh 7.6.2 at C:\Program Files\PowerShell\7\pwsh.exe ; python3 available.
- BOM-less LF writes:
  `[System.IO.File]::WriteAllText($p,($s -replace "`r`n","`n"),(New-Object System.Text.UTF8Encoding $false))`
- Surgical JSON block patches via literal `.Replace()`; verify with `ConvertFrom-Json`.
- Never two variables differing only by case; avoid arrays/List as hashtable values;
  avoid inline-if + format-operator paren nesting.
- Static checks: balanced braces/parens; case-collision scan; JSON via python json.
- Schemas: `$schema` 2020-12, `$id` imperium://schemas/<area>/<name>, `$comment` provenance,
  additionalProperties true.
- DO NOT touch the two intentional malformed fixtures:
  ORGANS\ADMINISTRATUM\BUNDLE_GATE\FIXTURES\v0_2_malformed_required_json\CLAIM_LEDGER.json ;
  SUPPORT\COMMON_IMPERIUM_SUPPORT\ROOT_IMPORTED_COMMON_SUPPORT\MATRIX_SPINE\FIXTURES\invalid_malformed_json_matrix.json

## 8. Roadmap & current state
- Phase M (Memoria): DONE. Deferred debt: add SHA256SUMS-set hash to MANIFEST.
- Phase O (Officio): DONE in order 2->1->3:
  step 2 reconciled Memoria role packs; step 1 stamped all 9 organs (ORGAN_CARD.json +
  ORGAN_CONTRACT.md); step 3 landed the Throne-gateway base.
- Phase A (Astronomicon orchestration): IN PROGRESS.
  - A1 DONE & landed: ASTRONOMICON inbound gate (astra_gate.py + 2 schemas), E3, runs
    FORM/COMPLETENESS/CORRECTNESS and emits an admission receipt.
  - DONE & landed: ADMINISTRATUM continuity assembler (continuity_assemble.py + schema +
    this doctrine), E3; assembles this Continuity Pack. Landed at master 325ac5bb.
  - Next: outbound validators + Servitor rework loop; Astra patch integrator; receipt-pack
    assembler; Throne supreme machine validator + precedent records; canon edit narrowing
    ADMINISTRATUM to archive+map and moving receipt assembly to Astra.
- Phase 4 (Servitor Runtime): later. Up to 4 isolated SERVITOR_PRIME CLI terminals/
  containers; organs lead, receipts, dry-run, pass-criteria gate, rework loop.
- North star: a full MetaOS IDE with an organ panel; core stays the bare 9-under-Throne
  terminal; plugins/APIs/trading+freelance agents live in the IDE harness, not the core.

## 9. How to resume in a new chat
1. Read this handoff fully. Note your role (LOGOS_PRIME or SERVITOR_PRIME) and the
   git_head stamped above.
2. Confirm the live HEAD matches the owner's latest git link before acting.
3. Pick the next pending item (section 8). Propose a pack; run the WARP flow with
   stage-gates. Ship real evidence. Keep the author convention. Output in Russian.
