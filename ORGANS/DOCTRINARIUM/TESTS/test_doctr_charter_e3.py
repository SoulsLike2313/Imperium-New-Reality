#!/usr/bin/env python3
"""DOCTR-CHARTER-0001: E3 tests for Doctrinarium charter.

12 tests covering:
  T01-T02: charter files exist (RU + EN)
  T03-T04: required sections present in both languages
  T05-T08: RU header fields canonical
  T09: NO_LLM_IN_PIPELINE declaration (RU + EN)
  T10: EN file contains English markers (not just Russian)
  T11: RU file is actually in Russian (>= 30% Cyrillic)
  T12: file sizes within sane bounds

Designed to run in a subprocess via _HARNESS/RUNNER/e3_runner.py.
PACK_ROOT env var is set by the runner; otherwise we walk up from __file__.
Exit 0 if all tests pass, 1 otherwise.

Stdlib only. No LLM. No network. Deterministic.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows cp1251 hosts.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Resolve PACK_ROOT
# ---------------------------------------------------------------------------

def resolve_pack_root() -> Path:
    env_root = os.environ.get("PACK_ROOT")
    if env_root:
        cand = Path(env_root).resolve()
        if cand.exists():
            return cand
    here = Path(__file__).resolve()
    # Walk up at most 10 levels, look for AGENTS.md + ORGANS/ as a marker.
    parents = [here.parent]
    for p in here.parents:
        parents.append(p)
    for i, cand in enumerate(parents):
        if i >= 10:
            break
        if (cand / "AGENTS.md").exists() and (cand / "ORGANS").is_dir():
            return cand
        if (cand / "ORGANS" / "_CORE_GOVERNANCE").is_dir():
            return cand
    return Path.cwd().resolve()


PACK_ROOT = resolve_pack_root()
CHARTER_DIR = PACK_ROOT / "DOCTRINARIUM" / "CHARTERS"
RU_FILE = CHARTER_DIR / "DOCTRINARIUM.md"
EN_FILE = CHARTER_DIR / "DOCTRINARIUM.en.md"

# ---------------------------------------------------------------------------
# Required sections (both files)
# ---------------------------------------------------------------------------
REQUIRED_SECTIONS = [
    "## \u00a70.",
    "## \u00a71.",
    "## \u00a72.",
    "## \u00a73.",
    "## \u00a74.",
    "## \u00a75.",
    "## \u00a76.",
    "## \u00a77.",
    "## \u00a78.",
    "## \u00a79.",
    "## \u00a710.",
    "## \u00a711.",
]

# ---------------------------------------------------------------------------
# Minimal test framework (stdlib-only)
# ---------------------------------------------------------------------------
TESTS_RUN = []
FAILED = []


def run_test(name: str, fn):
    TESTS_RUN.append(name)
    try:
        fn()
        print(f"PASS  {name}")
    except AssertionError as e:
        FAILED.append((name, str(e)))
        print(f"FAIL  {name}: {e}")
    except Exception as e:
        FAILED.append((name, f"{type(e).__name__}: {e}"))
        print(f"ERROR {name}: {type(e).__name__}: {e}")


def assert_true(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)


# ---------------------------------------------------------------------------
# Test bodies
# ---------------------------------------------------------------------------

def t01_ru_exists():
    assert_true(RU_FILE.exists(), f"RU charter not found at {RU_FILE}")
    assert_true(RU_FILE.is_file(), f"{RU_FILE} is not a regular file")


def t02_en_exists():
    assert_true(EN_FILE.exists(), f"EN charter not found at {EN_FILE}")
    assert_true(EN_FILE.is_file(), f"{EN_FILE} is not a regular file")


def t03_ru_sections():
    content = RU_FILE.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    assert_true(not missing, f"RU missing sections: {missing}")


def t04_en_sections():
    content = EN_FILE.read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SECTIONS if s not in content]
    assert_true(not missing, f"EN missing sections: {missing}")


def t05_ru_task_id():
    content = RU_FILE.read_text(encoding="utf-8")
    assert_true("DOCTR-CHARTER-0001" in content, "task_id 'DOCTR-CHARTER-0001' missing in RU header")


def t06_ru_version():
    content = RU_FILE.read_text(encoding="utf-8")
    assert_true("1.0.0" in content, "version '1.0.0' missing in RU header")
    assert_true("version:" in content, "'version:' label missing in RU header")


def t07_ru_schema():
    content = RU_FILE.read_text(encoding="utf-8")
    assert_true("imperium.charter.v0_1" in content, "schema_version 'imperium.charter.v0_1' missing")


def t08_ru_lineage():
    content = RU_FILE.read_text(encoding="utf-8")
    assert_true("d8027a8" in content, "lineage sha 'd8027a8' missing in RU header")


def t09_no_llm():
    ru = RU_FILE.read_text(encoding="utf-8")
    en = EN_FILE.read_text(encoding="utf-8")
    assert_true("NO_LLM_IN_PIPELINE" in ru, "NO_LLM_IN_PIPELINE declaration missing in RU")
    assert_true("NO_LLM_IN_PIPELINE" in en, "NO_LLM_IN_PIPELINE declaration missing in EN")


def t10_en_english():
    content = EN_FILE.read_text(encoding="utf-8")
    markers = ["Mission", "Authority", "Forbidden", "Canonical", "Charter"]
    missing = [m for m in markers if m not in content]
    assert_true(not missing, f"EN file missing English markers: {missing}")


def t11_ru_cyrillic():
    content = RU_FILE.read_text(encoding="utf-8")
    cyrillic_chars = sum(1 for ch in content if "\u0400" <= ch <= "\u04FF")
    total_letters = sum(1 for ch in content if ch.isalpha())
    ratio = (cyrillic_chars / total_letters) if total_letters else 0
    assert_true(
        ratio >= 0.30,
        f"RU cyrillic ratio {ratio:.2%} below 30% threshold (cyrillic={cyrillic_chars}, letters={total_letters})",
    )


def t12_size_bounds():
    ru_size = RU_FILE.stat().st_size
    en_size = EN_FILE.stat().st_size
    assert_true(5_000 <= ru_size <= 60_000, f"RU size {ru_size} out of bounds [5KB, 60KB]")
    assert_true(4_000 <= en_size <= 50_000, f"EN size {en_size} out of bounds [4KB, 50KB]")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print(f"PACK_ROOT = {PACK_ROOT}")
    print(f"RU_FILE   = {RU_FILE}")
    print(f"EN_FILE   = {EN_FILE}")
    print("---")

    tests = [
        ("T01_ru_exists", t01_ru_exists),
        ("T02_en_exists", t02_en_exists),
        ("T03_ru_sections", t03_ru_sections),
        ("T04_en_sections", t04_en_sections),
        ("T05_ru_task_id", t05_ru_task_id),
        ("T06_ru_version", t06_ru_version),
        ("T07_ru_schema", t07_ru_schema),
        ("T08_ru_lineage", t08_ru_lineage),
        ("T09_no_llm", t09_no_llm),
        ("T10_en_english", t10_en_english),
        ("T11_ru_cyrillic", t11_ru_cyrillic),
        ("T12_size_bounds", t12_size_bounds),
    ]

    for name, fn in tests:
        run_test(name, fn)

    print("---")
    passed = len(TESTS_RUN) - len(FAILED)
    status = "PASS" if not FAILED else "FAIL"
    summary = {
        "schema_version": "inq.e3_results.v0_1",
        "task_id": "DOCTR-CHARTER-0001",
        "test_file": "test_doctr_charter_e3.py",
        "tests_total": len(TESTS_RUN),
        "tests_passed": passed,
        "tests_failed": len(FAILED),
        "status": status,
        "failures": [{"test": n, "message": m} for (n, m) in FAILED],
    }
    print(json.dumps(summary, ensure_ascii=False))
    print(f"Total: {len(TESTS_RUN)}, Passed: {passed}, Failed: {len(FAILED)}")
    return 0 if not FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
