# ADMINISTRATUM — organ charter

**schema_version:** `imperium.administratum.v0_1`
**charter_version:** `1.0.0`
**parent_charter:** `imperium.astronomicon.v0_1` (ASTRONOMICON.en.md)
**ratified_by:** THRONE
**author_signed:** NOTION_OPUS (CHAT, Opus 4.8)
**storage:** `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.en.md` (+ `.md` for RU)

---

## §0. Nature of the organ (global principle for all 9 organs)

ADMINISTRATUM is a **script-first AI bot** capable of **influencing the task flow**.

- **“AI” means an autonomous bot** with rules, heuristics, statistics, and dictionaries. **“AI” does NOT mean LLM.**
- **The pipeline contains zero LLM calls.** LLMs exist only as **signers** of packs (NOTION_OPUS / CODEX / GROK) who CREATE packs from the outside. Inside organ hooks — deterministic scripts only.
- The organ influences the flow through **canonical verdicts** (see §5) that alter the course of Astra's cycle: HINT, BLOCK, RECORD.
- All organ decisions are **reproducible**: same inputs → same outputs.

This principle applies to all 9 organs of the Imperium and is enshrined in §0 of every charter.

## §1. Mission

ADMINISTRATUM is the **memory of the Imperium and its bookkeeper**. The organ performs four interlocking functions at once:

1. **Memory** — the single append-only journal of everything that ever happened in the task flow.
2. **Bookkeeping** — keeper of receipts, audit trail, ANOMALIES.
3. **Registry** — the single source of truth about tasks, agents, organs, rights, key rotations.
4. **Archivist-analyst** — deterministic retrospective: similar tasks, error patterns, statistics, anomalies.

Every organ of the Imperium is a heavy combat unit. The more ADMINISTRATUM CAN do deterministically, the more provable and clean the work of the entire Imperium becomes.

## §2. Hooks into Cycle (points of intervention)

ADMINISTRATUM plugs into Astra's cycle (`astra_cycle.py`) at four canonical points. Each hook is isolated through `subprocess` and operates under **FAIL_CLOSED**: a hook crash blocks the cycle.

| # | Hook | Cycle stage | Scripts | Can BLOCK? |
|---|---|---|---|---|
| H1 | `POST_ADMIT_HOOK` | right after `INBOUND ADMIT` | `admin_recall.py`, `admin_anomaly.py` | no (HINT only) |
| H2 | `PRE_PERMIT_HOOK` | before `PERMIT GRANTED` (THRONE) | `admin_quota.py`, `admin_drift.py` | **yes** (ADMIN_BLOCK_*) |
| H3 | `PRE_APPLY_HOOK` | after `PERMIT`, before `WARP_START` | final `admin_anomaly.py` | **yes** |
| H4 | `MEMORIZE_HOOK` | end of cycle (always, regardless of verdict) | `admin_memorize.py` | — (write only) |

## §3. Duties

ADMINISTRATUM is required, and only ADMINISTRATUM is entitled, to: maintain append-only `MEMORY/CURRENT.jsonl` with monthly rotation; guarantee atomic `_S3_RECEIPTS/<task_id>.work.{json,txt}`; keep `TASK_REGISTRY`, `AGENT_REGISTRY`, `ORGANS_LEDGER`; maintain AUDIT_TRAIL index; redact secrets via `REDACTION_PATTERNS.json`; run deterministic MEMORY_RECALL (Jaccard/keyword, no LLM); aggregate daily/weekly STATS; detect SCHEMA_DRIFT against `SCHEMA_KNOWN.json`; auto-tag tasks via `TAGS_DICT.json`.

## §4. Hard prohibitions

ADMINISTRATUM **never**: (1) mutates past records (append-only); (2) writes secrets/keys/tokens in clear text; (3) signs packs; (4) issues Throne-permit; (5) validates pack form (that is Astra); (6) blocks the flow silently — every ADMIN_BLOCK_* must carry `reason` + `recommendation`; (7) writes LLM output to `MEMORY/*.jsonl` without deterministic verification.

## §5. Canonical verdicts

11 canonical verdicts. Any other verdict is a charter violation.

### §5.1. Informational

- **ADMIN_RECORDED** — successful append to `MEMORY/CURRENT.jsonl`. Final verdict of any cycle at H4.
- **ADMIN_HINT_RECALL** — `admin_recall.py` found similar past tasks. HINT in the cycle banner; not blocking.
- **ADMIN_HINT_PATTERN** — `admin_recall.py` found a past CYCLE_FAIL_* with similar cause and its resolution. HINT; not blocking.

### §5.2. Blocking

- **ADMIN_BLOCK_RATE** — `rate_limit.per_author_hour` exceeded (default 30/hour).
- **ADMIN_BLOCK_LOOP** — `task_id` repeated more than 5 times in 24h (loop).
- **ADMIN_BLOCK_DUP** — same `payload_signature` 3+ times in a row (fake-retry).
- **ADMIN_BLOCK_COOLDOWN** — 3 consecutive CYCLE_FAIL_* from same author; cooldown 10 min.
- **ADMIN_BLOCK_BURST** — z-score of window volume > 3 vs daily baseline.
- **ADMIN_BLOCK_DRIFT** — `schema_version` absent from `SCHEMA_KNOWN.json`. Requires explicit ratification.

### §5.3. Service

- **ADMIN_OVERRIDDEN** — operator used `-ForceAdmin` to pass through ADMIN_BLOCK_*. Cycle continues; mandatory entry in `ANOMALIES.jsonl`.
- **ADMIN_FAILED_CLOSED** — ADMINISTRATUM itself crashed (rc≠0 or timeout). Cycle is blocked. Recovery only through owner intervention.

## §6. Receipt schema and memory record

### §6.1. Required fields in `MEMORY/CURRENT.jsonl`

Each record is one JSON line with at least: `utc`, `task_id`, `title`, `author`, `form`, `model`, `target_organ`, `verdict`, `reason`, `git{base_sha→new_sha}`, `payload_signature`, `stages[]`, `organs_seen[]`, `tags[]`, `receipt_path`, `admin_verdict`. Missing required field = validation error = `ADMIN_FAILED_CLOSED`.

### §6.2. Extensions to Astra's main receipt

Cycle's `_S3_RECEIPTS/<task>.work.json` is extended with `admin` block: `verdicts[]`, `hints[]`, `recall_top[]`, `quota_state`, `drift_diff`, `overrides[]`, `redactions_count`.

### §6.3. Separate BLOCK receipts

Each ADMIN_BLOCK_* additionally emits `_ADMINISTRATUM/BLOCKS/<task_id>.<utc>.json` with `reason`, `evidence`, `recommendation`, and counter snapshots for reproducibility.

## §7. HARNESS file architecture

ADMINISTRATUM stores all state in the HARNESS zone, never in master. Master holds only the charter and (after ADMIN-TOOLS-0001) the canonical scripts. See RU charter for ASCII tree.

Principles: append-only for all `.jsonl`; rotation by month via new file creation only; atomicity of receipts via `os.replace`.

## §8. Canonical scripts `ORGANS/ADMINISTRATUM/TOOLS/`

Declared here; delivered in ADMIN-TOOLS-0001:

`admin_init.py`, `admin_memorize.py`, `admin_recall.py`, `admin_quota.py`, `admin_anomaly.py`, `admin_drift.py`, `admin_redact.py`, `admin_stats.py`, `admin_query.py`, `admin_audit.py`, `admin_tag.py`.

All scripts — stdlib only. No external dependencies. No imports of `socket`, `urllib`, `requests`, `http.*`. Verified by T5.

## §9. Default thresholds (overridable)

| Parameter | Value | Verdict on excess |
|---|---|---|
| `per_author_hour` | 30 | `ADMIN_BLOCK_RATE` |
| `task_repeat_24h` | 5 | `ADMIN_BLOCK_LOOP` |
| `digest_repeat_inrow` | 3 | `ADMIN_BLOCK_DUP` |
| `fail_cooldown` | 3 FAIL → 10 min | `ADMIN_BLOCK_COOLDOWN` |
| `burst_zscore` | > 3.0 | `ADMIN_BLOCK_BURST` |
| `schema_drift` | any unknown schema_version | `ADMIN_BLOCK_DRIFT` |

Override: `-ForceAdmin` flag in `imp flow/apply` skips BLOCK but **mandatorily** writes to `ANOMALIES.jsonl`.

## §10. Invariants

- **I1 APPEND_ONLY** — every file in `_ADMINISTRATUM/` only grows.
- **I2 NO_SECRETS** — no `REDACTION_PATTERNS` match inside `MEMORY/*.jsonl`.
- **I3 NO_LLM_IN_PIPELINE** — no `admin_*.py` imports `socket`, `urllib`, `requests`, `http.*`.
- **I4 DETERMINISTIC** — same inputs → same outputs and verdicts.
- **I5 FAIL_CLOSED** — crash of any `admin_*.py` halts the cycle with `ADMIN_FAILED_CLOSED`.
- **I6 SIGNED_ONLY** — only packs with verified `imperium_provenance.verify` get written to memory.
- **I7 CANONICAL_ORGANS_ONLY** — `organs_seen[]` only contains the 9 canonical organs.
- **I8 OVERRIDE_LOGGED** — any `-ForceAdmin` mandatorily creates an `ANOMALIES.jsonl` entry.

## §11. Charter versioning

- SemVer `MAJOR.MINOR.PATCH`. MAJOR for verdicts/invariants; MINOR for new scripts/hooks; PATCH for textual edits.
- Every version is a separate pack, signed by Throne-permit.
- Storage: `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md` + `.en.md`, adjacent to `ASTRONOMICON.md`.
- Bilingual: RU and EN are mandatory and must stay in sync.

## §12. CHANGELOG

- **v1.0.0** (2026-06-20, NOTION_OPUS / CHAT / Opus 4.8) — First ratified version. 4 hooks, 11 verdicts, 8 invariants, 10 canonical scripts declared (delivery via separate pack ADMIN-TOOLS-0001).

## §13. Control tests

Runner: `ORGANS/ADMINISTRATUM/TESTS/test_admin_charter_e3.py`. Runs as WARP_TEST on every cycle touching the charter or organ scripts.

- **T1 ENFORCED** — charter structure: RU + EN, all 15 sections §0..§14, all 11 verdicts, all 8 invariants mentioned.
- **T2 ENFORCED** — `admin_*.py` not yet in canon (arrive in ADMIN-TOOLS-0001). Declared ENFORCED with SKIP until tools land.
- **T3 ENFORCED** — append-only smoke: open temp `.jsonl` in `"w"` mode via test wrapper → refuse/fail.
- **T4 ENFORCED** — redaction smoke: feed `api_key=ABC123` → output contains `[REDACTED]`.
- **T5 ENFORCED** — NO_NETWORK: assert no `import socket`, `urllib`, `requests`, `http` tokens in `admin_*.py`. Activated after ADMIN-TOOLS-0001.
- **T6 PLANNED v0_2** — RECALL by fixture.
- **T7 PLANNED v0_2** — DRIFT detection.
- **T8 PLANNED v0_2** — QUOTA simulation.
- **T9 PLANNED v0_3** — OVERRIDE flow.
- **T10 PLANNED v0_3** — full e2e cycle with all hooks.

Failure of any PLANNED test upon activation forces ratification of a new charter version with the discrepancy described in §12 CHANGELOG.

## §14. Relation to Astronomicon and Throne

- **Astronomicon** (`ASTRONOMICON.en.md`) — parent charter. Its cycle invokes Administratum hooks (§2). Any conflict is resolved in favor of Astronomicon.
- **Throne** — supreme validator. Any change to Administratum's charter requires Throne-permit. Any `ADMIN_BLOCK_*` can be contested only via Throne-override (`-ForceAdmin`), which is logged as anomaly.
- **Doctrinarium** — physical keeper of the charter. The file `DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md` is the single canonical source.
- **Other 6 organs** (Custodes, Inquisition, Mechanicus, Officio Agentis, Schola Imperialis, Strategium) are consumers of Administratum's memory. They read via `admin_query.py` and `admin_audit.py`, never write directly into `_ADMINISTRATUM/`.

---

*End of Administratum charter v1.0.0.*
