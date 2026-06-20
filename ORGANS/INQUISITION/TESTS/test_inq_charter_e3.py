#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# E3 runner for INQ-CHARTER-0001 (v2: hardened walk-up for Windows path depth)
# Win-safe contract:
#   - explicit utf-8 reconfigure of stdout/stderr (Windows cp1251 default)
#   - ASCII-only labels in stdout (no emoji)
#   - python (not python3) invocation expected in TASK_MANIFEST verify.cmd
#   - safe walk-up via lazy iteration of Path.parents (NO list-comp with explicit
#     index, which caused IndexError on shallow warp paths like E:\_warp_<task>\)
# Mode:
#   T1.1-T1.5 ENFORCED     (charter structure)
#   T2-T5    ENFORCED-SKIP (require INQ-TOOLS-0001 not yet landed)
#   T6-T10   PLANNED       (e2e tests, deferred to v0_3)
# Exit codes:
#   0 = PASS for all enforced tests; SKIPs are PASS-equivalent for cycle
#   1 = any FAIL
from __future__ import annotations
import io
import os
import sys
import json
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT = Path(__file__).resolve()
print(f"[runner] __file__ resolved to: {ROOT}")

# Safe walk-up: iterate Path.parents lazily, no explicit indexing.
# Path.parents is an indexable sequence on which negative or out-of-range
# indexing raises IndexError; iterating it is safe and stops at filesystem root.
REPO = None
parents_checked = []
for cand in ROOT.parents:
    parents_checked.append(str(cand))
    if (cand / "DOCTRINARIUM" / "CHARTERS" / "INQUISITION.md").is_file():
        REPO = cand
        break

if REPO is None:
    print("FAIL: cannot locate DOCTRINARIUM/CHARTERS/INQUISITION.md")
    print("      directories searched (from nearest parent upward):")
    for p in parents_checked:
        print(f"        - {p}")
    sys.exit(1)

print(f"[runner] repo root: {REPO}")

RU = REPO / "DOCTRINARIUM" / "CHARTERS" / "INQUISITION.md"
EN = REPO / "DOCTRINARIUM" / "CHARTERS" / "INQUISITION.en.md"

results = []

def add(name: str, status: str, detail: str = "") -> None:
    results.append((name, status, detail))

# ----- T1.1: RU + EN exist -----
if RU.is_file() and EN.is_file():
    add("T1.1_FILES_PRESENT", "PASS", f"RU={RU.name} EN={EN.name}")
else:
    add("T1.1_FILES_PRESENT", "FAIL", f"RU.is_file={RU.is_file()} EN.is_file={EN.is_file()}")

try:
    ru_text = RU.read_text(encoding="utf-8") if RU.is_file() else ""
except Exception as exc:
    ru_text = ""
    add("T1.1_FILES_PRESENT", "FAIL", f"RU read_text exception: {exc!r}")

try:
    en_text = EN.read_text(encoding="utf-8") if EN.is_file() else ""
except Exception as exc:
    en_text = ""
    add("T1.1_FILES_PRESENT", "FAIL", f"EN read_text exception: {exc!r}")

# ----- T1.2: version 1.0.0 in both -----
if "v1.0.0" in ru_text and "v1.0.0" in en_text:
    add("T1.2_VERSION_1_0_0", "PASS", "v1.0.0 present in both")
else:
    add("T1.2_VERSION_1_0_0", "FAIL", "v1.0.0 missing in RU or EN")

# ----- T1.3: NO_LLM_IN_PIPELINE in both -----
if "NO_LLM_IN_PIPELINE" in ru_text and "NO_LLM_IN_PIPELINE" in en_text:
    add("T1.3_NO_LLM_IN_PIPELINE", "PASS", "clause present in both")
else:
    add("T1.3_NO_LLM_IN_PIPELINE", "FAIL", "NO_LLM_IN_PIPELINE clause missing")

# ----- T1.4: H1..H5 hook IDs present in both -----
hook_ids = ["H1", "H2", "H3", "H4", "H5"]
missing_hooks_ru = [h for h in hook_ids if h not in ru_text]
missing_hooks_en = [h for h in hook_ids if h not in en_text]
if not missing_hooks_ru and not missing_hooks_en:
    add("T1.4_FIVE_HOOKS", "PASS", "H1..H5 in RU and EN")
else:
    add("T1.4_FIVE_HOOKS", "FAIL", f"missing RU={missing_hooks_ru} EN={missing_hooks_en}")

# ----- T1.5: invariants (>=8) and verdicts (12 required) -----
invariant_count = sum(
    1 for i in range(1, 13)
    if (f"I{i} " in ru_text) or (f"I{i}." in ru_text) or (f"**I{i}" in ru_text)
)
verdicts_required = [
    "INQ_OK",
    "INQ_HINT_SECRETS",
    "INQ_HINT_PI",
    "INQ_BLOCK_SECRETS",
    "INQ_BLOCK_PI",
    "INQ_BLOCK_TRUST",
    "INQ_BLOCK_BAN",
    "INQ_BLOCK_AUDIT",
    "INQ_BLOCK_REDACT_FAIL",
    "INQ_BLOCK_PURGE_NOT_READY",
    "INQ_OVERRIDDEN",
    "INQ_FAILED_CLOSED",
]
missing_verdicts = [v for v in verdicts_required if v not in ru_text]
if invariant_count >= 8 and not missing_verdicts:
    add("T1.5_INVARIANTS_AND_VERDICTS", "PASS",
        f"invariants={invariant_count} verdicts={len(verdicts_required)}")
else:
    add("T1.5_INVARIANTS_AND_VERDICTS", "FAIL",
        f"invariants={invariant_count}, missing_verdicts={missing_verdicts}")

# ----- T2..T5: ENFORCED-SKIP (tools not yet shipped) -----
add("T2_INQ_SECRETS_SMOKE", "SKIP", "requires INQ-TOOLS-0001 (planned next pack)")
add("T3_INQ_PI_SCAN_SMOKE", "SKIP", "requires INQ-TOOLS-0001")
add("T4_INQ_TRUST_SMOKE",   "SKIP", "requires INQ-TOOLS-0001")
add("T5_INQ_AUDIT_SMOKE",   "SKIP", "requires INQ-TOOLS-0001")

# ----- T6..T10: PLANNED for v0_3 -----
add("T6_E2E_SECRETS_FIXTURE",     "SKIP", "PLANNED v0_3: synthetic sk-/AKIA fixture")
add("T7_E2E_PI_FIXTURE",          "SKIP", "PLANNED v0_3: 'ignore previous'/'system:' fixture")
add("T8_E2E_TRUST_RECOMPUTE",     "SKIP", "PLANNED v0_3: 3 packs per author")
add("T9_E2E_PURGE_DORMANT",       "SKIP", "PLANNED v0_3: scan only, CORE_READY=false")
add("T10_E2E_FORENSIC_TRACE",     "SKIP", "PLANNED v0_3: synthetic task_id with 3 verdicts")

# ----- Summary -----
fails = sum(1 for _, s, _ in results if s == "FAIL")
passes = sum(1 for _, s, _ in results if s == "PASS")
skips = sum(1 for _, s, _ in results if s == "SKIP")

print("=" * 60)
print("INQ-CHARTER-0001 E3 runner v2 (Win-safe, hardened walk-up)")
print("=" * 60)
for name, status, detail in results:
    print(f"[{status:4}] {name}  {detail}")
print("-" * 60)
print(f"PASS={passes} FAIL={fails} SKIP={skips}")
print("=" * 60)

sys.exit(0 if fails == 0 else 1)
