# MECHANICUS — organ charter

**schema_version:** `imperium.mechanicus.v0_1`
**charter_version:** `1.0.0`
**parent_charter:** `imperium.astronomicon.v0_1` (ASTRONOMICON.en.md)
**sibling_charters:** `imperium.administratum.v0_1` (ADMINISTRATUM.en.md)
**ratified_by:** THRONE
**author_signed:** NOTION_OPUS (CHAT, Opus 4.8)
**storage:** `DOCTRINARIUM/CHARTERS/MECHANICUS.en.md` (+ `.md` for RU)

---

## §0. Nature of the organ (global principle for all 9 organs)

MECHANICUS is a **script-first AI bot** capable of **influencing the task flow**.

- **“AI” means an autonomous bot** with rules, AST parsing, statics, and regression baselines. **“AI” does NOT mean LLM.**
- **The pipeline contains zero LLM calls.** LLMs exist only as **signers** of packs (NOTION_OPUS / CODEX / GROK) from the outside. Inside the organ hooks — deterministic scripts only.
- The organ influences the flow through **canonical verdicts** (see §5): HINT, BLOCK, OVERRIDDEN.
- All decisions are **reproducible**: same inputs → same outputs.

This principle applies to all 9 organs of the Imperium and is enshrined in §0 of every charter.

## §1. Mission

MECHANICUS is the **engineer and keeper of the mechanisms of the Imperium**. The organ performs five interlocking functions:

1. **Canon-scripts lifecycle** — lint, unit-test, regressions of every `admin_*.py` / `astra_*.py` / `inq_*.py` / `imperium_*.py`.
2. **Environment** — stdlib-only enforcement, Python pins (Windows 3.12 / sandbox 3.13), dependency drift control.
3. **HARNESS maintenance** — rotation of `_ADMINISTRATUM/MEMORY/*.jsonl`, vacuum of orphaned receipts, GC of stale warp-worktrees.
4. **Schema migrations** — registry and application of registered migrations of `SCHEMA_KNOWN.json`, receipt formats, charter versions.
5. **E3-runner meta-checks** — `test_*_e3.py` must be Windows-safe (utf8 reconfigure + ASCII labels + `python` command, not `python3`).

Every organ of the Imperium is a heavy combat unit. The more MECHANICUS CAN do deterministically, the higher the engineering quality of the whole Imperium.

## §2. Hooks into Cycle (points of intervention)

MECHANICUS plugs into `astra_cycle.py` via seven canonical hooks. All hooks are isolated through `subprocess` and operate under **FAIL_CLOSED**: a hook crash blocks the cycle.

| # | Hook | Cycle stage | Scripts | Can BLOCK? |
|---|---|---|---|---|
| H1 | `POST_ADMIT_HOOK` | right after `INBOUND ADMIT` | `mech_depscan.py` | no (HINT only) |
| H2 | `PRE_PERMIT_HOOK` | before `PERMIT GRANTED` (THRONE) | `mech_lint.py`, `mech_depscan.py`, `mech_envpin.py` | **yes** (MECH_BLOCK_*) |
| H3 | `WARP_TEST_EXTEND` | inside `WARP_TEST` stage | `mech_test.py`, `mech_regress.py` | **yes** |
| H4 | `PRE_APPLY_HOOK` | after PERMIT, before COMMIT | `mech_meta_e3.py` | **yes** |
| H5 | `POST_LAND_HOOK` | after `LAND` + `PUSH` | `mech_vacuum.py`, `mech_compact.py` (dry-run by default) | no |
| H6 | `SCHEDULED_TICK` | daily tick outside the cycle | `mech_vacuum.py`, `mech_compact.py` | no |
| H7 | `ON_DEMAND` | manual owner invocation | `mech_build.py`, `mech_migrate.py` | — (manual) |

## §3. Duties

MECHANICUS is required, and only MECHANICUS is entitled, to:

1. **mech_lint** — AST inspection of canon scripts: forbidden imports, unused names, style violations.
2. **mech_test** — run unit tests in every `ORGANS/*/TESTS/test_*.py`.
3. **mech_regress** — a fixed fixture set (`REGRESS/FIXTURES/`), compare output against goldens (`REGRESS/GOLDENS/`).
4. **mech_depscan** — token-scan of sources for `socket`, `urllib`, `requests`, `http.*` (enforcement of invariant I3 NO_LLM_IN_PIPELINE from Administratum).
5. **mech_envpin** — Python version check (MAJOR.MINOR match against `ENV/PYTHON_PIN.json`) and module whitelist (`ENV/DEPS_ALLOWED.json`).
6. **mech_compact** — rotation of `_ADMINISTRATUM/MEMORY/CURRENT.jsonl` into `YYYY-MM.jsonl` on the first day of the month.
7. **mech_vacuum** — GC of warp-worktrees older than `vacuum_age_days` (default 30) and orphaned receipts without matching `TASK_REGISTRY` entries.
8. **mech_migrate** — application of registered migrations from `_MECHANICUS/MIGRATIONS/<schema>/<from>_<to>.py` (ON_DEMAND only).
9. **mech_meta_e3** — verification that `test_*_e3.py` is Windows-safe: contains `sys.stdout.reconfigure(encoding="utf-8")`, has ASCII-only printable labels, uses `python` (not `python3`) in `verify.cmd`.
10. **mech_build** — assembly of zip packs by canon structure (like `imp_pack`, but organ-scoped, with auto-generated `TASK_MANIFEST.json` skeleton).

## §4. Hard prohibitions

MECHANICUS **never**: (1) signs packs; (2) issues Throne-permit; (3) validates pack form (that is Astronomicon); (4) writes to `_ADMINISTRATUM/MEMORY/` or registries (that is Administratum); (5) blocks silently — every `MECH_BLOCK_*` must carry `reason` AND `recommendation`; (6) commits to master directly (everything in warp-worktree); (7) imports `socket`, `urllib`, `requests`, `http.*`; (8) writes LLM-call output into registries, reports, or goldens; (9) runs `mech_vacuum` / `mech_compact` in destructive mode without explicit `--confirm` (default is `--dry-run`).

## §5. Canonical verdicts

12 canonical verdicts. Any other verdict is a charter violation.

### §5.1. Positive

- **MECH_OK** — all hook checks passed.

### §5.2. Informational (HINT)

- **MECH_HINT_DEPSCAN** — early warning at H1 POST_ADMIT about suspicious imports. HINT in the cycle banner; not blocking.
- **MECH_HINT_LINT** — non-blocking style warnings. HINT; not blocking.

### §5.3. Blocking

- **MECH_BLOCK_LINT** — AST/style violation (unused name, duplicate import, naming violation, etc.). Raised at H2 PRE_PERMIT.
- **MECH_BLOCK_DEPSCAN** — forbidden import found (`socket`, `urllib`, `requests`, `http`). Pre-emptively enforces Administratum invariant I3 NO_LLM_IN_PIPELINE.
- **MECH_BLOCK_NETWORK** — DEPSCAN equivalent focused on network modules. Fires on `import socket` or any network call.
- **MECH_BLOCK_ENVPIN** — Python MAJOR.MINOR does not match `ENV/PYTHON_PIN.json`. Defends against `python3 vs python` regressions (historical bug of ASTRON-CHARTER v1).
- **MECH_BLOCK_TEST** — `mech_test` returned rc≠0 for at least one unit test.
- **MECH_BLOCK_REGRESS** — actual script output diverges from `REGRESS/GOLDENS/`. Any diff blocks (regress_diff_threshold = 0).
- **MECH_BLOCK_TIMEOUT** — a test/check exceeded `test_timeout_sec` (default 60).
- **MECH_BLOCK_META** — `test_*_e3.py` is not Windows-safe: missing `sys.stdout.reconfigure(...)`, contains Cyrillic in test labels, or uses `python3` in `verify.cmd`. This invariant saved the LAND of ASTRON-CHARTER v2.

### §5.4. Service

- **MECH_OVERRIDDEN** — operator used `-ForceMech` to bypass `MECH_BLOCK_*`. Cycle continues; mandatory entry in `_MECHANICUS/ANOMALIES.jsonl`.
- **MECH_FAILED_CLOSED** — MECHANICUS itself crashed (rc≠0 or hook timeout). Cycle is blocked. Recovery only through owner intervention.

## §6. Receipt schema and mech_report.json

### §6.1. `mech_report.json` fields (per-hook result)

Each hook run produces `_MECHANICUS/REPORTS/YYYY-MM-DD/mech_<task>_<hook>_<utc>.json` with: `utc`, `task_id`, `hook_point` (H1..H7), `command`, `scripts_scanned[]`, `lint_findings[]` (objects of `{file, line, severity, code, message}`), `depscan_imports[]`, `test_results[]` (objects of `{test_name, rc, duration_sec, stdout_tail, stderr_tail}`), `regress_diff` (`{golden_path, actual_path, unified_diff}` or `null`), `env_info` (`{python_version, platform, cwd, executable}`), `verdict` (one of 12), `reason`, `recommendation`, `evidence_path`, `exit_code`, `duration_sec`. Missing required field = validation error = `MECH_FAILED_CLOSED`.

### §6.2. Extension of the Astra receipt

`_S3_RECEIPTS/<task>.work.json` is extended with a `mech` block: `verdicts[]`, `hints[]`, `findings_count`, `reports[]` (list of `mech_report.json` paths).

### §6.3. Separate BLOCK receipts

Each `MECH_BLOCK_*` additionally emits `_MECHANICUS/BLOCKS/<task_id>.<utc>.json` with the full `mech_report` + cycle-stage reference + recommendation.

## §7. HARNESS file architecture

MECHANICUS keeps all of its state in the HARNESS zone, never in master. Master only holds the charter and (after `MECH-TOOLS-0001`) the canonical scripts. See RU charter for the ASCII tree.

Principles: append-only for all `.jsonl`; monthly rotation via new file creation; atomicity via `os.replace`; GOLDENS immutable without explicit migration.

## §8. Canonical scripts `ORGANS/MECHANICUS/TOOLS/`

Declared here; delivered in `MECH-TOOLS-0001`:

`mech_init.py`, `mech_lint.py`, `mech_test.py`, `mech_regress.py`, `mech_depscan.py`, `mech_envpin.py`, `mech_compact.py`, `mech_vacuum.py`, `mech_migrate.py`, `mech_meta_e3.py`, `mech_build.py`.

**CLI style (hybrid):**
- Every script is self-sufficient: `python mech_lint.py <pack_dir> [--strict]` (positional pack_dir + flags, like `imperium_provenance.py`).
- Optional entry point `mechanicus.py <subcmd> ...` is equivalent to a direct call: `mechanicus.py lint <pack_dir>` ≡ `mech_lint.py <pack_dir>`.

All scripts — **stdlib only**. No external dependencies. No imports of `socket`, `urllib`, `requests`, `http.*`. Enforced by T4 and invariant I2.

## §9. Default thresholds (overridable)

| Parameter | Value | Verdict on violation |
|---|---|---|
| `lint_severity_threshold` | error (zero tolerance) | `MECH_BLOCK_LINT` |
| `test_timeout_sec` | 60 | `MECH_BLOCK_TIMEOUT` |
| `regress_diff_threshold` | 0 (any diff = block) | `MECH_BLOCK_REGRESS` |
| `envpin_strict_match` | MAJOR.MINOR | `MECH_BLOCK_ENVPIN` |
| `vacuum_age_days` | 30 | (not blocking; cleanup) |
| `compact_period` | monthly (day 1) | (not blocking; rotation) |
| `depscan_forbidden_count` | 0 | `MECH_BLOCK_DEPSCAN` / `MECH_BLOCK_NETWORK` |

Override: `-ForceMech` flag in `imp flow/apply` bypasses BLOCK but **mandatorily** writes to `_MECHANICUS/ANOMALIES.jsonl`.

## §10. Invariants

- **I1 DETERMINISTIC** — same inputs → same verdicts.
- **I2 NO_NETWORK** — no `mech_*.py` imports `socket`, `urllib`, `requests`, `http.*`.
- **I3 STDLIB_ONLY** — only Python's standard library. No pip dependencies.
- **I4 FAIL_CLOSED** — a crash of any `mech_*.py` halts the cycle with `MECH_FAILED_CLOSED`.
- **I5 SIGNED_ONLY** — MECHANICUS only operates on packs that passed `imperium_provenance.verify`.
- **I6 CANONICAL_ORGANS_ONLY** — `target_organ` from the 9 canonical organs only.
- **I7 OVERRIDE_LOGGED** — every `-ForceMech` mandatorily creates an entry in `ANOMALIES.jsonl`.
- **I8 GOLDEN_IMMUTABLE** — `REGRESS/GOLDENS/` cannot be changed without a registered migration in `MIGRATIONS/`.
- **I9 NO_MASTER_MUTATE** — all MECHANICUS operations happen in a warp-worktree. Direct commits to master are forbidden.

## §11. Charter versioning

- SemVer `MAJOR.MINOR.PATCH`. MAJOR for verdict/invariant changes; MINOR for new hooks/scripts; PATCH for textual edits.
- Every version is a separate pack, signed by Throne-permit.
- Storage: `DOCTRINARIUM/CHARTERS/MECHANICUS.md` + `.en.md`, adjacent to `ASTRONOMICON.md` and `ADMINISTRATUM.md`.
- Bilingual: RU and EN are mandatory and must stay in sync.

## §12. CHANGELOG

- **v1.0.0** (2026-06-20, NOTION_OPUS / CHAT / Opus 4.8) — First ratified version. 7 hooks, 12 verdicts, 9 invariants, 10 canonical scripts declared (delivery via separate pack `MECH-TOOLS-0001`).

## §13. Control tests

Runner: `ORGANS/MECHANICUS/TESTS/test_mech_charter_e3.py`. Runs as WARP_TEST on every cycle touching the charter or the organ scripts.

- **T1 ENFORCED** — charter structure: RU + EN, all 15 sections §0..§14, all 12 verdicts, all 9 invariants, the NO_LLM_IN_PIPELINE principle.
- **T2 ENFORCED-SKIP** — `mech_*.py` CLI smoke (activates with `MECH-TOOLS-0001`).
- **T3 ENFORCED-SKIP** — `mech_lint` smoke (fixture with a forbidden import).
- **T4 ENFORCED-SKIP** — `mech_depscan` smoke (fixture with `import socket`).
- **T5 ENFORCED-SKIP** — `mech_meta_e3` smoke (fixture without `utf8 reconfigure`).
- **T6 PLANNED v0_2** — `mech_test` across all `ORGANS/*/TESTS/`.
- **T7 PLANNED v0_2** — `mech_regress` against GOLDEN baselines.
- **T8 PLANNED v0_2** — `mech_envpin` (Python mismatch detection).
- **T9 PLANNED v0_3** — `mech_vacuum` dry-run on fake warp-worktrees.
- **T10 PLANNED v0_3** — full e2e: pack with a broken script → PRE_PERMIT → `MECH_BLOCK_*`.

Failure of any PLANNED test upon activation forces ratification of a new charter version with the discrepancy described in §12 CHANGELOG.

## §14. Relation to other organs

- **Astronomicon** (`ASTRONOMICON.en.md`) — parent charter. Its cycle invokes the Mechanicus hooks (§2). Any conflict resolves in favor of Astronomicon.
- **Administratum** (`ADMINISTRATUM.en.md`) — sibling organ. Mechanicus works on physical mechanisms (scripts, environment, files), Administratum on facts (memory, registries, statistics). Mechanicus **does not write** to `_ADMINISTRATUM/`, but **reads** through `admin_query.py` / `admin_audit.py` for run statistics.
- **Throne** — supreme validator. Any change to the Mechanicus charter requires Throne-permit. Any `MECH_BLOCK_*` can only be contested through Throne-override (`-ForceMech`), logged as an anomaly.
- **Doctrinarium** — physical keeper of the charter. The file `DOCTRINARIUM/CHARTERS/MECHANICUS.md` is the single canonical source.
- **Remaining 5 organs** (Custodes, Inquisition, Officio Agentis, Schola Imperialis, Strategium) — consumers of Mechanicus checks. Every one of their canonical scripts (once built) passes `mech_lint`, `mech_depscan`, `mech_envpin`, `mech_meta_e3`.

---

*End of Mechanicus charter v1.0.0.*
