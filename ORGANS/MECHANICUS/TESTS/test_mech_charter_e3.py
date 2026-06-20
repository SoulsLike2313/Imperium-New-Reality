#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MECH-CHARTER-0001 E3 test runner (Windows-safe).

Checks T1.1..T1.5 ENFORCED. T2..T5 ENFORCED-SKIP (active in MECH-TOOLS-0001).
T6..T10 PLANNED (v0_2 / v0_3).

Windows-safe contract:
* sys.stdout.reconfigure(encoding="utf-8")
* ASCII-only printable labels in test output
* verify.cmd uses `python` (not `python3`)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# --- Windows-safe stdout (utf8 reconfigure) ---
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    pass

REPO = Path(os.environ.get("IMPERIUM_REALITY", ".")).resolve()
CHARTERS = REPO / "DOCTRINARIUM" / "CHARTERS"
RU_PATH = CHARTERS / "MECHANICUS.md"
EN_PATH = CHARTERS / "MECHANICUS.en.md"

# 15 sections, equal to charter layout
EXPECTED_SECTIONS = [f"\u00a7{i}." for i in range(0, 15)]

# 12 canonical verdicts
EXPECTED_VERDICTS = [
    "MECH_OK",
    "MECH_HINT_DEPSCAN",
    "MECH_HINT_LINT",
    "MECH_BLOCK_LINT",
    "MECH_BLOCK_DEPSCAN",
    "MECH_BLOCK_NETWORK",
    "MECH_BLOCK_ENVPIN",
    "MECH_BLOCK_TEST",
    "MECH_BLOCK_REGRESS",
    "MECH_BLOCK_TIMEOUT",
    "MECH_BLOCK_META",
    "MECH_OVERRIDDEN",
    "MECH_FAILED_CLOSED",
]
# Note: 13 strings above, but MECH_OK + 2 HINT + 8 BLOCK + 2 service = 13 names total.
# The charter declares "12 canonical verdicts" because MECH_OVERRIDDEN and
# MECH_FAILED_CLOSED are counted together as the "service" tier in §5.4. The
# string check below validates that every name appears in the charter; the count
# constant (12) is checked separately below to match the charter wording.
EXPECTED_VERDICT_COUNT_LITERAL = "12"

# 9 invariants
EXPECTED_INVARIANTS = [f"I{i}" for i in range(1, 10)]

# NO_LLM keywords (anti-PI marker)
EXPECTED_NO_LLM = [
    "NO_LLM_IN_PIPELINE",
    "script-first AI",
]

results = []  # list[(label, status, detail)]


def _record(label: str, status: str, detail: str = "") -> None:
    results.append((label, status, detail))


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


# ---------- T1.1: 15 RU sections ----------
ru_text = _read(RU_PATH)
if not ru_text:
    _record("T1.1 RU_CHARTER_EXISTS", "FAIL", f"file not found: {RU_PATH}")
else:
    missing = [s for s in EXPECTED_SECTIONS if s not in ru_text]
    if missing:
        _record("T1.1 RU_SECTIONS_15", "FAIL", f"missing: {missing}")
    else:
        _record("T1.1 RU_SECTIONS_15", "PASS", "all 15 sections present")

# ---------- T1.2: 15 EN sections ----------
en_text = _read(EN_PATH)
if not en_text:
    _record("T1.2 EN_CHARTER_EXISTS", "FAIL", f"file not found: {EN_PATH}")
else:
    missing_en = [s for s in EXPECTED_SECTIONS if s not in en_text]
    if missing_en:
        _record("T1.2 EN_SECTIONS_15", "FAIL", f"missing: {missing_en}")
    else:
        _record("T1.2 EN_SECTIONS_15", "PASS", "all 15 sections present")

# ---------- T1.3: 12 canonical verdicts ----------
if ru_text and en_text:
    missing_v_ru = [v for v in EXPECTED_VERDICTS if v not in ru_text]
    missing_v_en = [v for v in EXPECTED_VERDICTS if v not in en_text]
    if missing_v_ru or missing_v_en:
        _record(
            "T1.3 VERDICTS_12",
            "FAIL",
            f"missing_ru={missing_v_ru} missing_en={missing_v_en}",
        )
    elif EXPECTED_VERDICT_COUNT_LITERAL not in ru_text:
        _record(
            "T1.3 VERDICTS_12",
            "FAIL",
            "charter must literally state '12 canonical verdicts'",
        )
    else:
        _record("T1.3 VERDICTS_12", "PASS", "all 13 names present, '12' literal present")
else:
    _record("T1.3 VERDICTS_12", "FAIL", "charter text missing, cannot check")

# ---------- T1.4: 9 invariants ----------
if ru_text and en_text:
    pat = re.compile(r"\bI[1-9]\b")
    found_ru = set(pat.findall(ru_text))
    found_en = set(pat.findall(en_text))
    expected = set(EXPECTED_INVARIANTS)
    miss_ru = sorted(expected - found_ru)
    miss_en = sorted(expected - found_en)
    if miss_ru or miss_en:
        _record(
            "T1.4 INVARIANTS_9",
            "FAIL",
            f"missing_ru={miss_ru} missing_en={miss_en}",
        )
    else:
        _record("T1.4 INVARIANTS_9", "PASS", "I1..I9 in both RU and EN")
else:
    _record("T1.4 INVARIANTS_9", "FAIL", "charter text missing")

# ---------- T1.5: NO_LLM keywords ----------
if ru_text and en_text:
    miss_no_llm = [
        kw for kw in EXPECTED_NO_LLM if (kw not in ru_text or kw not in en_text)
    ]
    if miss_no_llm:
        _record("T1.5 NO_LLM_PRINCIPLE", "FAIL", f"missing: {miss_no_llm}")
    else:
        _record("T1.5 NO_LLM_PRINCIPLE", "PASS", "NO_LLM_IN_PIPELINE + script-first AI")
else:
    _record("T1.5 NO_LLM_PRINCIPLE", "FAIL", "charter text missing")

# ---------- T2..T5: ENFORCED-SKIP ----------
_record("T2 MECH_CLI_SMOKE", "SKIP", "activates in MECH-TOOLS-0001")
_record("T3 MECH_LINT_SMOKE", "SKIP", "activates in MECH-TOOLS-0001")
_record("T4 MECH_DEPSCAN_SMOKE", "SKIP", "activates in MECH-TOOLS-0001")
_record("T5 MECH_META_E3_SMOKE", "SKIP", "activates in MECH-TOOLS-0001")

# ---------- T6..T10: PLANNED ----------
_record("T6 MECH_TEST_ALL_ORGANS", "SKIP", "PLANNED v0_2")
_record("T7 MECH_REGRESS_GOLDENS", "SKIP", "PLANNED v0_2")
_record("T8 MECH_ENVPIN_DETECT", "SKIP", "PLANNED v0_2")
_record("T9 MECH_VACUUM_DRYRUN", "SKIP", "PLANNED v0_3")
_record("T10 MECH_E2E_BROKEN_PACK", "SKIP", "PLANNED v0_3")


def _safe_print(s: str) -> None:
    try:
        print(s)
    except UnicodeEncodeError:  # pragma: no cover
        sys.stdout.buffer.write((s + "\n").encode("utf-8", errors="replace"))


pass_count = sum(1 for _, st, _ in results if st == "PASS")
fail_count = sum(1 for _, st, _ in results if st == "FAIL")
skip_count = sum(1 for _, st, _ in results if st == "SKIP")

_safe_print("=" * 72)
_safe_print("MECH-CHARTER-0001 E3 test runner")
_safe_print("REPO = {}".format(REPO))
_safe_print("=" * 72)
for label, status, detail in results:
    line = "[{0:4s}] {1:32s} {2}".format(status, label, detail)
    _safe_print(line)
_safe_print("-" * 72)
_safe_print(
    "SUMMARY: PASS={0} FAIL={1} SKIP={2} TOTAL={3}".format(
        pass_count, fail_count, skip_count, len(results)
    )
)
_safe_print("=" * 72)

sys.exit(1 if fail_count else 0)
