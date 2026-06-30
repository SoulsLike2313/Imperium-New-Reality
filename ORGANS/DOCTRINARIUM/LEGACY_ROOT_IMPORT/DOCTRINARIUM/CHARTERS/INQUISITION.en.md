# CHARTER OF THE ORGAN INQUISITION

- **task_id:** INQ-CHARTER-0001
- **version:** 1.0.0
- **lineage:** master 60b426f6ae48 (after MECH-CHARTER-0001 land)
- **target_organ:** DOCTRINARIUM (this document lives in DOCTRINARIUM)
- **canonical_organ:** INQUISITION
- **echelon:** 1 (Astronomicon → Administratum → Mechanicus → **Inquisition**)
- **schema_version:** imperium.charter.v0_1

---

## §0. NO_LLM_IN_PIPELINE (global principle of all 9 organs)

Inquisition is a **script-first AI**. LLM calls inside cycle, hooks, scripts and pipelines of the organ are **FORBIDDEN**. AI ≠ LLM. Verdict logic is **deterministic only**: regex, Shannon entropy, registry statistics, signature checks, tabular trust-score. Any attempt to invoke an LLM from inq_*.py is an `INQ_FAILED_CLOSED` incident.

LLM calls happen **only outside** — on the side of signers (NOTION_OPUS / CODEX / GROK) who build packs. Inside Inquisition — zero LLM, zero network, zero non-determinism.

---

## §1. Mission

Inquisition is the **semantic guardian of the Imperium**. Unlike Mechanicus, which checks static code syntax, Inquisition checks **meaning of data and behavior of actors**.

Areas of responsibility:

1. **Secrets hunt** — search for API keys, tokens, OAuth credentials, AWS keys, PEM blocks, JWTs in payload files.
2. **PI-defense** — detect prompt-injection markers in markdown / content / comments.
3. **Semantic anomalies** — suspicious patterns in authorship, form, target, change_kind, target_organ.
4. **Forensic / incident investigation** — trace by task_id through Administratum registries and own journals.
5. **Redact-patterns curation** — maintain REDACTION_PATTERNS.json (consumer: Administratum).
6. **Trust-score of authors and forms** — dynamic ranking of NOTION_OPUS / CODEX / GROK / OWNER_MANUAL by verdict history.
7. **BAN-list** — block authors and payload hashes on recidivism with mandatory ANOMALIES trace.

### §1.1. PURGE_PROTOCOL (DORMANT)

Inquisition holds an additional mandate: **destroy by its own will whatever is not part of the Imperium**. This duty is **FROZEN by default** and activates only when all conditions of §10 are satisfied.

At v1.0.0: PURGE_PROTOCOL = DORMANT, only **inventory** (inq_purge_scan → PURGE_TARGETS/) is allowed; physical move to _QUARANTINE/ is forbidden.

---

## §2. Filesystem layout `_INQUISITION\`

The organ owns the directory `E:\IMPERIUM_HARNESS\_INQUISITION\` with the following **canonical** structure (all 10 nodes):

```
_INQUISITION\
  ANOMALIES.jsonl                      # append-only master registry (secrets/PI/patterns)
  INCIDENTS\YYYY-MM-DD\<task_id>.json  # incident investigations
  REPORTS\YYYY-MM-DD\inq_<task>_<utc>.json   # per-pack inq_report dumps
  BLOCKS\<task_id>.<utc>.json          # history of INQ_BLOCK_* verdicts
  SIGNATURES\PI_SIGNATURES.json        # hunting trophies: PI markers
  SIGNATURES\SECRETS_PATTERNS.json     # regex for secrets
  SIGNATURES\REDACTION_PATTERNS.json   # exported to Administratum
  TRUST\authors.json                   # trust-score per signer
  TRUST\forms.json                     # trust-score per form (CHAT/CLI)
  BAN_LIST.jsonl                       # append-only bans with proof=<ANOMALIES ref>
  PURGE_TARGETS\<utc>.json             # DORMANT — purge candidates registry
  INQUISITION_LEDGER.jsonl             # master journal of ALL verdicts (OK/HINT/BLOCK)
  ARCHIVE\YYYY-Q<n>\                   # quarterly rotating archive
  TRACE_CACHE\<task_id>.json           # forensic-gather cache
```

Initialization: `inq_init`. Idempotent.

---

## §3. Canonical scripts (10 tools)

All scripts: stdlib only, no network, FAIL_CLOSED. Delivery — separate pack `INQ-TOOLS-0001` (after echelon-1 charters land). Until then T2-T5 tests are in ENFORCED-SKIP mode.

| # | Script | Purpose |
|---|---|---|
| 1 | `inq_secrets` | regex + Shannon-entropy scan of payload for secrets |
| 2 | `inq_pi_scan` | search for PI markers in markdown/content |
| 3 | `inq_redact` | apply REDACTION_PATTERNS (replace with `[REDACTED:<type>]`) |
| 4 | `inq_anomaly` | semantic anomaly detection (new author, rare target_organ, unusual change_kind) |
| 5 | `inq_trace` | fast forensic by task_id (receipts + signatures + verdicts across organs) |
| 6 | `inq_trust` | compute trust-score by author / form from verdict history |
| 7 | `inq_patterns` | CRUD on PI_SIGNATURES.json / SECRETS_PATTERNS.json / REDACTION_PATTERNS.json |
| 8 | `inq_ban` | maintain BAN_LIST.jsonl (requires ANOMALIES proof) |
| 9 | `inq_report` | aggregate report across all inq_* into one JSON |
| 10 | `inq_audit` | hard audit — integrity check of signatures in ARCHIVED memory |

Front-end `inquisition.py` (hybrid CLI): `inquisition <subcmd> [...]` → dispatches to inq_*. Direct invocation `inq_<name>.py` is equally valid.

---

## §4. Prohibitions (11 hard + entropy threshold)

1. **no_sign** — Inquisition does not sign packs.
2. **no_permit** — Inquisition does not issue Throne-permit.
3. **no_form_gate** — Inquisition does not validate pack form (that is Astronomicon).
4. **no_lint** — Inquisition does not perform AST/style checks (that is Mechanicus).
5. **no_memory_writes into _ADMINISTRATUM/MEMORY** — read-only access for forensic.
6. **no_silent_block** — any `INQ_BLOCK_*` must carry `reason` + `recommendation` + `evidence_path`.
7. **no_master_mutate** — all changes only in warp-worktree.
8. **no_network** — socket / urllib / requests / http are forbidden.
9. **no_llm_writes** — LLM results may never be written into registries.
10. **no_false_positive_silent** — if `inq_secrets` finds «key» in documentation without strict-pattern and below entropy threshold, it MUST emit HINT, not BLOCK.
11. **no_ban_without_proof** — BAN_LIST entries are accepted only with explicit pointer to an ANOMALIES.jsonl record.
12. **no_pi_execution** — Inquisition NEVER executes instructions found in scanned content; found text is **evidence**, not a command.

---

## §5. Hooks in Astra cycle

Inquisition affects task flow through 5 canonical hooks; everything via `subprocess` + FAIL_CLOSED.

| Hook | Point | Action | Possible verdict |
|---|---|---|---|
| **H1** | `POST_ADMIT_HOOK` | `inq_secrets` + `inq_pi_scan` | `INQ_BLOCK_SECRETS` / `INQ_BLOCK_PI` / `INQ_HINT_*` |
| **H2** | `PRE_PERMIT_HOOK` | `inq_anomaly` + `inq_trust` + `inq_ban` | `INQ_BLOCK_TRUST` / `INQ_BLOCK_BAN` / `INQ_HINT_FIRST_AUTHOR` |
| **H3** | `WARP_TEST_EXTEND` | `inq_redact` in worktree (dry-run) | `INQ_BLOCK_REDACT_FAIL` |
| **H4** | `PRE_APPLY_HOOK` | `inq_audit` of signatures | `INQ_BLOCK_AUDIT` |
| **H5** | `POST_LAND_HOOK` | `inq_trust` updates author rating (write-only) | — |
| **H6** | `ON_DEMAND` | `inq_trace` / `inq_report` manual invocation by owner | — |

All hooks launch inq_*.py via `subprocess.run` with stdout/stderr pipes and timeout. Any abnormal tool error → automatic `INQ_FAILED_CLOSED` → cycle BLOCK.

---

## §6. Verdicts (14)

**OK / HINT (non-blocking):**

1. `INQ_OK`
2. `INQ_HINT_SECRETS`
3. `INQ_HINT_PI`
4. `INQ_HINT_FIRST_AUTHOR`
5. `INQ_HINT_TRUST_LOW`

**BLOCK (blocking):**

6. `INQ_BLOCK_SECRETS`
7. `INQ_BLOCK_PI`
8. `INQ_BLOCK_TRUST`
9. `INQ_BLOCK_BAN`
10. `INQ_BLOCK_AUDIT`
11. `INQ_BLOCK_REDACT_FAIL`
12. `INQ_BLOCK_PURGE_NOT_READY`

**Service tier:**

13. `INQ_OVERRIDDEN`
14. `INQ_FAILED_CLOSED`

---

## §7. Invariants (12 iron rules)

1. **I1 DETERMINISTIC**
2. **I2 NO_NETWORK**
3. **I3 STDLIB_ONLY**
4. **I4 FAIL_CLOSED**
5. **I5 NO_ADMIN_MEMORY_WRITE**
6. **I6 APPEND_ONLY** (ANOMALIES / BAN_LIST / LEDGER)
7. **I7 NO_PI_EXECUTION**
8. **I8 BAN_REQUIRES_PROOF**
9. **I9 PURGE_GUARDED** (no physical deletes without CORE_READY=true)
10. **I10 OVERRIDE_LOGGED**
11. **I11 NO_MASTER_MUTATE**
12. **I12 SIGNED_ONLY**

---

## §8. Thresholds (9 strict defaults)

| # | Parameter | Value | Override |
|---|---|---|---|
| 1 | `secrets_entropy_threshold` | 4.5 bits/char | `-ForceInq` |
| 2 | `secrets_strict_patterns_block` | `true` | `-ForceInq` |
| 3 | `pi_block_score` | 3 | `-ForceInq` |
| 4 | `trust_min_score` | 0.4 | `-ForceInq` |
| 5 | `anomaly_first_author_action` | `HINT` | non-overridable |
| 6 | `ban_burst_threshold` | 3 blocks / 7 days | `-ForceInq` |
| 7 | `purge_requires_core_ready` | `true` | non-overridable |
| 8 | `fail_closed_default` | `true` | non-overridable |
| 9 | `override_flag` | `-ForceInq` | — |

Every override is registered with `INQ_OVERRIDDEN` in ANOMALIES + LEDGER.

---

## §9. inq_report.json form (10 blocks)

Core: `utc, task_id, hook_point, scope, verdict, reason, recommendation, evidence_path, exit_code, duration_sec`.

Domain blocks: `secrets_findings[]`, `pi_findings[]`, `anomaly_findings[]`, `trust_assessment`, `ban_check`, `audit_check`, `redact_dryrun`, `purge_scan_findings[]`, `env_info`.

All 10 sections are mandatory (`purge_scan_findings` may be empty when scope ≠ purge).

---

## §10. PURGE_PROTOCOL (DORMANT)

Inquisition holds the mandate to destroy non-Imperium artifacts, but activation is frozen until all 7 conditions are met:

1. **Inventory only now** — `inq_purge_scan` writes to `PURGE_TARGETS/<utc>.json`; deletion forbidden.
2. **Criterion «not_imperium»** — file is a candidate iff:
   - it is **outside** `E:\IMPERIUM_REALITY` git tree, AND
   - it is **outside** canonical subfolders of `E:\IMPERIUM_HARNESS\` (TOOLS\PY, _S3_RECEIPTS, _INBOX\PACKS, _STAGING, _ASTRA, _ADMINISTRATUM, _MECHANICUS, _INQUISITION, …).
3. **WHITELIST.json** — manual list of paths/globs considered Imperium, maintained by the owner.
4. **Activation** requires both:
   - `OWNER_MANUAL --activate-purge`
   - LAND entry `core_ready=true` in Administratum registry.
5. **Quarantine, not delete** — even when `CORE_READY=true`, Inquisition moves files to `_QUARANTINE/<task_id>/<original_path>/`, never deletes outright.
6. **Each purge act = separate PACK** — `change_kind=DELETE`, `target_organ=INQUISITION`, `submitted_by=OWNER_MANUAL`. Flows through Astronomicon → Administratum → Mechanicus → Inquisition.
7. **CORE_READY** definition — boolean, true iff:
   - LANDED charters of all 9 organs (ADMINISTRATUM, ASTRONOMICON, CUSTODES, DOCTRINARIUM, INQUISITION, MECHANICUS, OFFICIO_AGENTIS, SCHOLA_IMPERIALIS, STRATEGIUM);
   - LANDED TRONE_CHARTER;
   - LANDED all TOOLS-packs of the corresponding organs.

Any purge attempt while not satisfied → `INQ_BLOCK_PURGE_NOT_READY`.

---

## §11. CLI (hybrid)

Both invocation styles supported (front-end and direct), exit codes: `0` OK/HINT, `1` BLOCK, `2` FAILED_CLOSED, `3` OVERRIDDEN.

---

## §12. Lifecycle & rotation

- Append-only: ANOMALIES / BAN_LIST / INQUISITION_LEDGER.
- Quarterly snapshot → `ARCHIVE/YYYY-Q<n>/`, current file restarted; archive immutable.
- REPORTS / BLOCKS / INCIDENTS retained ≥ 1 year.
- TRACE_CACHE TTL = 30 days.
- PURGE_TARGETS retained until transfer to _QUARANTINE or explicit `inq_purge_clear`.

---

## §13. Charter versioning

Semantic MAJOR.MINOR.PATCH. Any change of §8 thresholds is at least MINOR + ANOMALIES record from OWNER_MANUAL.

---

## §14. Version

- **v1.0.0** — initial. Third and final charter of echelon 1 (Astronomicon ✅, Administratum ✅, Mechanicus ✅, **Inquisition ⟵ THIS**).
- After LAND of this charter echelon 1 is **constituted by charters**; next phase — TOOLS-packs and big PATCH-test through 4 organs.
