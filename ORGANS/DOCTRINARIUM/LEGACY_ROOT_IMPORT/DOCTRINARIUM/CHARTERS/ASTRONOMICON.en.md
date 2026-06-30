# ASTRONOMICON Charter

- schema_version: `imperium.astronomicon.v0_1`
- charter_version: `1.0.0`
- language: en (ru — see `ASTRONOMICON.md`)
- signed_by: NOTION_OPUS (CHAT / Opus 4.8); Throne permit at land time

---

## §1. Mission

ASTRONOMICON is the **keeper of the task**. Sole registrar and validator of every pack before canonization into `master`.
No pack lands without completing Astra's cycle.

## §2. Modes

### §2.1. HAND_PACK
- Source: OWNER_MANUAL or NOTION_OPUS, form filled by hand (`PATCH_PACK_FORM`).
- Astra **signs** (provenance), registers, and executes the cycle herself.
- Reporting is self-contained (receipt + memory).

### §2.2. AUTO_PACK
- Source: Servitor (CODEX / GROK), form `TASK_PACK_FORM`.
- Astra **registers** the task-pack. **Without a registry entry, Servitor cannot proceed.**
- All 9 organs participate (full elaboration after all charters and the Throne matrix exist).

## §3. Validation cycle

### §3.1. Admission (3 gates)
1. `INBOUND` — `astra_gate.validate(pack)`: schema, payload, evidence_level, change_kind.
2. `PROVENANCE` — `imperium_provenance.verify(pack)`: signature valid; author ∈ `{NOTION_OPUS, CODEX, GROK, OWNER_MANUAL}`.
3. `PERMIT` — Throne permit = `GRANTED`.

### §3.2. Execution
4. `WARP_START` — create `warp/<task_id>` branch and worktree outside master.
5. `INTEGRATE` — apply `integration.map` (file → target path).
6. `WARP_TEST` — `verify.cmd` with `rc=0`.
7. `COMMIT` — commit in warp branch with `author=signer`.

### §3.3. Landing
8. `PRE_LAND` — drop untracked collisions (warp branch is authoritative).
9. `LAND` — `git merge --squash warp/<task_id>` into master, commit.
10. `PUSH` — `origin master` (if remote configured).
11. `CLEANUP` — remove worktree + branch.

### §3.4. Recording
12. `RECEIPT` — `receipt.json` + `receipt.txt` in `_S3_RECEIPTS\<task_id>.work.{json,txt}`.
13. `MEMORY` — append-only entry into `ADMINISTRATUM_MEMORY.jsonl`.

### §3.5. Task passport (log format)
Mandatory fields in the passport block:
- From (author / form / model)
- Contour (WINDOWS_PC / SANDBOX / …)
- Permit (THRONE = GRANTED)
- Validation (ASTRONOMICON gate INBOUND + WARP_TEST → verdict)
- Memory (ADMINISTRATUM receipt index)
- Land (`base_sha → land_sha`)
- Result (verdict)

## §4. Hard prohibitions

1. **No push** without green `WARP_TEST`.
2. **No secrets/keys** in receipt or memory.
3. **Never emit `CYCLE_OK`** on any red stage.
4. **Never touch master directly** — only via `warp/<task_id>` + squash.
5. **Never bypass** `gate` / `provenance` / `permit` under any circumstance.
6. **Never sign third-party packs or modify payload** (validator role).
   - **Exception:** in `HAND_PACK` Astra may sign the pack herself (see §2.1).

## §5. Canonical verdicts

Every red verdict carries a **`reason`** and a **`recommendation`**.

| Verdict | Triggered when |
|---|---|
| `CYCLE_OK` | Full cycle passed, master advanced |
| `CYCLE_DRYRUN_OK` | Dry-run green, waiting for `apply` |
| `CYCLE_REJECTED_GATE` | `INBOUND` failed (schema/payload/evidence) |
| `CYCLE_REJECTED_PROVENANCE` | Signature broken, no author, or identity mismatch |
| `CYCLE_REJECTED_PERMIT` | Throne ≠ GRANTED |
| `CYCLE_FAIL_INTEGRATE` | `integration.map` failed to apply |
| `CYCLE_FAIL_WARP_TEST` | `verify.cmd` rc ≠ 0 |
| `CYCLE_FAIL_LAND` | merge/squash failed even after `PRE_LAND` |
| `CYCLE_FAIL_PUSH` | remote rejected (auth/conflict/network) |
| `TASK_NOT_REGISTERED` | Servitor came with a `task_id` not in registry |
| `TASK_PENDING` | Registered but not yet validated |
| `TASK_BLOCKED_SERVITOR` | Explicit Servitor stop (Astra refused) |

## §6. Receipt schema (minimum)

See Russian version §6 for the canonical JSON example. Principle: **human and machine** must equally understand what happened and why.

## §7. "Core × Harness" architecture (Windows-style)

- **Core (REALITY / master):** canon only — charter, tools, receipts of completed tasks.
- **Harness (HARNESS):** task registry, forms, work-orders, working state, temporary files, test runs.

Rule: **state never lives in the core**. Only canonized results.

### §7.1. Harness layout
- `E:\IMPERIUM_HARNESS\_ASTRA\TASK_REGISTRY.jsonl` — append-only task index.
- `E:\IMPERIUM_HARNESS\_ASTRA\TASKS\<task_id>\` — task details + pack draft + work-order.
- `E:\IMPERIUM_HARNESS\_S3_RECEIPTS\<task_id>.work.{json,txt}` — work receipts (later canonized into master).
- `E:\IMPERIUM_HARNESS\_S3_RECEIPTS\ADMINISTRATUM_MEMORY.jsonl` — append-only memory.

## §8. Servitor blocking (AUTO_PACK)

Servitor is started strictly with `--task-id <id>`:
1. Servitor approaches Astra with `task_id`.
2. Astra checks `TASK_REGISTRY.jsonl`.
3. Decision:
   - not found → `TASK_NOT_REGISTERED` → **STOP** (reason: "Astra refused: task not registered").
   - found but not validated → `TASK_PENDING` → **STOP** (reason: "Astra refused: task awaiting validation").
   - found and validated → issue a **work-order** (signed JSON) → Servitor proceeds.

## §9. Pack forms

- **`PATCH_PACK_FORM`** — for `HAND_PACK`. See `ASTRONOMICON_FORMS/PATCH_PACK_FORM.md` + `.template.json`.
- **`TASK_PACK_FORM`** — for `AUTO_PACK`. See `ASTRONOMICON_FORMS/TASK_PACK_FORM.md` + `.template.json`.

Filled form → NOTION_OPUS polish → gate-passing pack.

## §10. Invariants (always true)

1. Never touch master without warp: always squash from `warp/<task_id>`.
2. Every pack is signed. `HAND_PACK`: Astra signs (delegated authorship). `AUTO_PACK`: Servitor signs.
3. Secrets/keys **never** reach receipt or memory.
4. Core × Harness: master holds canon and receipts only; all state lives in HARNESS.
5. No task in registry → Servitor stops (Astra blocks).
6. `ADMINISTRATUM_MEMORY` is append-only and never rewritten.

## §11. Charter versioning

- `charter_version` (semver): `1.0.0` → `1.1.0` (additive) → `2.0.0` (breaking).
- `schema_version`: `imperium.astronomicon.v0_1` → `v0_2` (structural changes).
- `CHANGELOG` lives inside the charter (§12).
- Each new version is **a normal pack** (`ASTRON-CHARTER-000N`) passing Astra's cycle (meta-validation).
- Each version requires a Throne permit. After all 9 organs are described, the **Throne matrix** governs charter approvals.

## §12. CHANGELOG

- **v1.0.0** (first edition): modes `HAND_PACK`/`AUTO_PACK`, receipt format, pack forms (PATCH/TASK), invariants, tests `cycle` + `collision` as `ENFORCED`, `check-task`/`HAND_E2E`/`form→pack` as `PLANNED`.

## §13. Control tests

| # | Test | Status v1.0.0 | Plan |
|---|---|---|---|
| 1 | E3 cycle 4/4 (land / discard / tamper / unsigned) | **ENFORCED** | — |
| 2 | E3 PRE_LAND collision (untracked dropped, land succeeds) | **ENFORCED** | — |
| 3 | E3 check-task → `TASK_NOT_REGISTERED` | PLANNED | v0_2 |
| 4 | E3 HAND_PACK end-to-end (Astra signs + executes) | PLANNED | v0_3 |
| 5 | E3 form → pack (filled form yields a gate-passing pack) | PLANNED | v0_3 |

Green `ENFORCED` tests = precondition for accepting any pack from ASTRONOMICON.
Periodic runs → red test → rewrite the corresponding charter section or Astra tool.
Run history stored versionwise in `E:\IMPERIUM_HARNESS\_ASTRA\TEST_RUNS\<utc>.json`.

## §14. Doctrinarium

Charter is stored under:
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON.md` (RU, working).
- `DOCTRINARIUM/CHARTERS/ASTRONOMICON.en.md` (EN, translation).

Doctrinarium owns storage, versioning, and periodic test runs. Astra executes; Doctrinarium keeps charters clean and operational.
