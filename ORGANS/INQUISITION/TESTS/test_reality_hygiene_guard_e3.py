#!/usr/bin/env python3
"""REALITY-HYGIENE-GUARD-0001 E3 tests.

These tests protect the source checkout from repo-local Inquisition runtime
negative-experience receipts when a canonical sibling HARNESS exists.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
from pathlib import Path

FAILS: list[tuple[str, str]] = []


def _assert(cond: bool, tag: str, detail: str) -> None:
    if not cond:
        FAILS.append((tag, detail))
        print(f"[FAIL] {tag}: {detail}")
    else:
        print(f"[ ok ] {tag}")


def _load_inq_report():
    here = Path(__file__).resolve()
    tools = here.parents[1] / "TOOLS" / "inq_report.py"
    spec = importlib.util.spec_from_file_location("inq_report_guard_under_test", tools)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {tools}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_block_verdict(mod, reports_dir: Path, task_id: str = "TEST-HYGIENE-GUARD") -> None:
    vb = mod.VerdictBuilder(
        tool="inq_hygiene_guard_test",
        task_id=task_id,
        author="OWNER_MANUAL",
        stage="H6_ON_DEMAND",
    )
    vb.block("HYGIENE_GUARD_TEST", "intentional block for negative-experience routing test")
    _d, _path, ec = vb.write(reports_dir=str(reports_dir), also_stdout=False)
    _assert(ec == 1, f"{task_id}.exit", f"expected BLOCK exit 1, got {ec}")


def T1_sibling_harness_receives_negative_experience() -> None:
    mod = _load_inq_report()
    root = Path(tempfile.mkdtemp(prefix="imp_hygiene_guard_"))
    try:
        reality = root / "IMPERIUM_REALITY"
        harness = root / "IMPERIUM_HARNESS"
        reports = reality / "ORGANS" / "INQUISITION" / "REPORTS"
        reports.mkdir(parents=True)
        harness.mkdir(parents=True)
        (reality / "ORGANS" / "INQUISITION").mkdir(parents=True, exist_ok=True)
        (reality / "DOCTRINARIUM").mkdir()
        _write_block_verdict(mod, reports, "TEST-HYGIENE-SIBLING")
        expected = harness / "_NEGATIVE_EXPERIENCE" / "TEST-HYGIENE-SIBLING"
        legacy = reality / "_HARNESS" / "_NEGATIVE_EXPERIENCE" / "TEST-HYGIENE-SIBLING"
        _assert(expected.exists(), "T1.external_harness_written", f"missing {expected}")
        _assert(not legacy.exists(), "T1.no_repo_local_negative", f"unexpected {legacy}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def T2_explicit_env_override_wins() -> None:
    mod = _load_inq_report()
    root = Path(tempfile.mkdtemp(prefix="imp_hygiene_guard_env_"))
    old = os.environ.get("IMPERIUM_NEGATIVE_EXPERIENCE_DIR")
    try:
        target = root / "CUSTOM_NEG"
        os.environ["IMPERIUM_NEGATIVE_EXPERIENCE_DIR"] = str(target)
        reality = root / "IMPERIUM_REALITY"
        reports = reality / "ORGANS" / "INQUISITION" / "REPORTS"
        reports.mkdir(parents=True)
        (reality / "ORGANS" / "INQUISITION").mkdir(parents=True, exist_ok=True)
        (reality / "DOCTRINARIUM").mkdir()
        _write_block_verdict(mod, reports, "TEST-HYGIENE-ENV")
        _assert((target / "TEST-HYGIENE-ENV").exists(), "T2.env_override_written", f"missing {target}")
    finally:
        if old is None:
            os.environ.pop("IMPERIUM_NEGATIVE_EXPERIENCE_DIR", None)
        else:
            os.environ["IMPERIUM_NEGATIVE_EXPERIENCE_DIR"] = old
        shutil.rmtree(root, ignore_errors=True)


def T3_gitignore_contains_negative_experience_guard() -> None:
    here = Path(__file__).resolve()
    root = None
    for cand in here.parents:
        if (cand / ".gitignore").exists() and (cand / "ORGANS").exists():
            root = cand
            break
    _assert(root is not None, "T3.root_found", f"root not found from {here}")
    if root is None:
        return
    text = (root / ".gitignore").read_text(encoding="utf-8")
    _assert("REALITY-HYGIENE-GUARD-0001" in text, "T3.guard_marker", "marker missing")
    _assert("_HARNESS/_NEGATIVE_EXPERIENCE/" in text, "T3.root_pattern", "root pattern missing")
    _assert("**/_HARNESS/_NEGATIVE_EXPERIENCE/" in text, "T3.deep_pattern", "deep pattern missing")


def main() -> int:
    for fn in [
        T1_sibling_harness_receives_negative_experience,
        T2_explicit_env_override_wins,
        T3_gitignore_contains_negative_experience_guard,
    ]:
        print(f"\n--- {fn.__name__} ---")
        try:
            fn()
        except Exception as exc:
            FAILS.append((fn.__name__, f"EXCEPTION: {type(exc).__name__}: {exc}"))
            print(f"[FAIL] {fn.__name__}: EXCEPTION: {type(exc).__name__}: {exc}")
    print("\n=== SUMMARY ===")
    if FAILS:
        print(f"FAILED: {len(FAILS)}")
        for tag, detail in FAILS:
            print(f"  - {tag}: {detail}")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
