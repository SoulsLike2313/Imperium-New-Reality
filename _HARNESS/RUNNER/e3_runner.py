#!/usr/bin/env python3
"""E3 runner v3 -- bulletproof test execution harness for INQ-class packs.

Discovers all test_*.py files under <PACK_ROOT>/ORGANS/*/TESTS/ and runs each in
a subprocess, capturing stdout/stderr/returncode. Aggregates into:

  _HARNESS/_RUNS/<utc>/EXECUTION_LOG.txt  -- human-readable log
  _HARNESS/_RUNS/<utc>/RESULTS.json       -- machine-readable, schema inq.e3_results.v0_1

Bulletproof features (lessons from INQ-CHARTER attempt 1 IndexError):
  * Lazy parents walk (NO `parents[i]` indexing -- iterate `for cand in parents`).
  * Max walk depth capped at 10.
  * Path.cwd() appended as fallback when __file__ is shallow.
  * Forces UTF-8 stdout/stderr (matters on Windows cp1251).
  * CI/local detection via env (CI, GITHUB_ACTIONS, GITLAB_CI, JENKINS_URL).
  * Default per-test timeout 60s, override via --timeout.
  * subprocess env: PYTHONUNBUFFERED=1, PYTHONIOENCODING=utf-8, PACK_ROOT=<root>.
  * Deterministic test discovery via sorted(glob).
  * Exit 0 if all tests pass, else 1; exit 2 on harness FAIL_CLOSED.

Usage:
  python3 _HARNESS/RUNNER/e3_runner.py                # auto-discover root, all tests
  python3 _HARNESS/RUNNER/e3_runner.py --organ INQUISITION
  python3 _HARNESS/RUNNER/e3_runner.py --select test_inq_tools_e3.py
  python3 _HARNESS/RUNNER/e3_runner.py --timeout 120
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = "inq.e3_results.v0_1"
MAX_DEPTH = 10
DEFAULT_TIMEOUT_SEC = 60


def _force_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _utc_now_compact() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_pack_root(p: Path) -> bool:
    if (p / "TASK_MANIFEST.json").exists():
        return True
    if (p / "PROVENANCE.json").exists():
        return True
    if (p / "_HARNESS").is_dir() and (p / "ORGANS").is_dir():
        return True
    return False


def find_pack_root(start: Optional[Path] = None, max_depth: int = MAX_DEPTH) -> Path:
    """Lazy parents walk with max-depth cap and Path.cwd() fallback.

    Never indexes parents[i] -- that pattern caused IndexError on shallow paths
    (lesson from INQ-CHARTER-0001 attempt 1).
    """
    if start is None:
        try:
            start = Path(__file__).resolve()
        except Exception:
            start = Path.cwd().resolve()
    if start.is_file():
        start = start.parent

    seen = set()
    depth = 0
    # candidates: start itself + parents + cwd fallback
    chain: List[Path] = [start]
    for cand in start.parents:
        chain.append(cand)
    cwd = Path.cwd().resolve()
    if cwd not in chain:
        chain.append(cwd)

    for cand in chain:
        if depth > max_depth:
            break
        depth += 1
        if cand in seen:
            continue
        seen.add(cand)
        try:
            if _is_pack_root(cand):
                return cand
        except (OSError, PermissionError):
            continue

    raise RuntimeError(
        f"PACK_ROOT not found within depth {max_depth} starting from {start}"
    )


def _detect_environment() -> Dict[str, Any]:
    is_ci = any(
        os.environ.get(k)
        for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "BUILDKITE")
    )
    return {
        "is_ci": bool(is_ci),
        "ci_provider": next(
            (k for k in ("GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "BUILDKITE") if os.environ.get(k)),
            None,
        ),
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
        "pythonioencoding": os.environ.get("PYTHONIOENCODING"),
    }


def discover_tests(pack_root: Path, organ: Optional[str] = None, select: Optional[List[str]] = None) -> List[Path]:
    organs_dir = pack_root / "ORGANS"
    out: List[Path] = []
    if not organs_dir.is_dir():
        return out
    organ_dirs = (
        [organs_dir / organ] if organ else sorted(p for p in organs_dir.iterdir() if p.is_dir())
    )
    for od in organ_dirs:
        tests_dir = od / "TESTS"
        if not tests_dir.is_dir():
            continue
        for f in sorted(tests_dir.glob("test_*.py")):
            if select and f.name not in select:
                continue
            out.append(f)
    return out


def run_one(
    test_path: Path,
    pack_root: Path,
    timeout_sec: int,
) -> Dict[str, Any]:
    started = time.monotonic()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PACK_ROOT"] = str(pack_root)
    rc: int
    out_text = ""
    err_text = ""
    timed_out = False
    try:
        proc = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=str(pack_root),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
        )
        rc = proc.returncode
        out_text = proc.stdout
        err_text = proc.stderr
    except subprocess.TimeoutExpired as te:
        rc = 124
        timed_out = True
        out_text = (te.stdout or b"").decode("utf-8", "replace") if isinstance(te.stdout, (bytes, bytearray)) else (te.stdout or "")
        err_text = f"TIMEOUT after {timeout_sec}s"
    except Exception as e:
        rc = 2
        err_text = f"HARNESS_RUN_ERROR: {type(e).__name__}: {e}"
    elapsed = round(time.monotonic() - started, 3)
    return {
        "test_path": str(test_path.relative_to(pack_root)),
        "return_code": rc,
        "timed_out": timed_out,
        "elapsed_sec": elapsed,
        "stdout_tail": _tail(out_text, 4000),
        "stderr_tail": _tail(err_text, 2000),
        "passed": (rc == 0) and not timed_out,
    }


def _tail(s: str, n: int) -> str:
    if not s:
        return ""
    if len(s) <= n:
        return s
    return "...[truncated]...\n" + s[-n:]


def write_outputs(pack_root: Path, run_dir: Path, env_info: Dict[str, Any], results: List[Dict[str, Any]]) -> Dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    overall = "PASS" if failed == 0 and total > 0 else ("FAIL" if total > 0 else "NO_TESTS")

    log_path = run_dir / "EXECUTION_LOG.txt"
    res_path = run_dir / "RESULTS.json"

    lines: List[str] = []
    lines.append(f"=== E3 RUNNER v3 ===")
    lines.append(f"timestamp_utc : {_utc_now_iso()}")
    lines.append(f"pack_root     : {pack_root}")
    lines.append(f"platform      : {env_info['platform']}")
    lines.append(f"python        : {env_info['python']}")
    lines.append(f"is_ci         : {env_info['is_ci']} ({env_info.get('ci_provider')})")
    lines.append(f"cwd           : {env_info['cwd']}")
    lines.append("")
    lines.append(f"--- {total} test file(s) ---")
    for r in results:
        status = "PASS" if r["passed"] else ("TIMEOUT" if r["timed_out"] else f"FAIL(rc={r['return_code']})")
        lines.append(f"  [{status:>15}] {r['elapsed_sec']:>6.2f}s  {r['test_path']}")
        if r["stdout_tail"]:
            for ln in r["stdout_tail"].rstrip().splitlines()[-30:]:
                lines.append(f"    | {ln}")
        if r["stderr_tail"] and not r["passed"]:
            for ln in r["stderr_tail"].rstrip().splitlines()[-20:]:
                lines.append(f"    ! {ln}")
    lines.append("")
    lines.append(f"=== SUMMARY: {overall} ({passed}/{total} passed, {failed} failed) ===")

    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    machine = {
        "schema_version": SCHEMA,
        "timestamp_utc": _utc_now_iso(),
        "pack_root": str(pack_root),
        "env": env_info,
        "summary": {"total": total, "passed": passed, "failed": failed, "overall": overall},
        "tests": results,
    }
    res_path.write_text(json.dumps(machine, ensure_ascii=False, indent=2), encoding="utf-8")
    return machine


def main() -> int:
    _force_utf8()
    ap = argparse.ArgumentParser(description="E3 runner v3 (bulletproof)")
    ap.add_argument("--pack-root", default=None, help="Override auto-discovery")
    ap.add_argument("--organ", default=None, help="Restrict to one organ (e.g. INQUISITION)")
    ap.add_argument("--select", action="append", default=None, help="Specific test file name(s); repeatable")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    try:
        pack_root = Path(args.pack_root).resolve() if args.pack_root else find_pack_root()
    except Exception as e:
        sys.stderr.write(f"FAIL_CLOSED: cannot resolve PACK_ROOT: {e}\n")
        return 2

    env_info = _detect_environment()
    tests = discover_tests(pack_root, organ=args.organ, select=args.select)
    if not tests:
        sys.stderr.write(f"NO_TESTS: nothing matched under {pack_root}/ORGANS/{args.organ or '*'}/TESTS/\n")
        run_dir = pack_root / "_HARNESS" / "_RUNS" / _utc_now_compact()
        write_outputs(pack_root, run_dir, env_info, [])
        return 2

    results: List[Dict[str, Any]] = []
    for t in tests:
        if not args.quiet:
            sys.stdout.write(f"[run] {t.relative_to(pack_root)} ...\n")
            sys.stdout.flush()
        results.append(run_one(t, pack_root, args.timeout))

    run_dir = pack_root / "_HARNESS" / "_RUNS" / _utc_now_compact()
    summary = write_outputs(pack_root, run_dir, env_info, results)
    if not args.quiet:
        sys.stdout.write(json.dumps(summary["summary"], ensure_ascii=False) + "\n")
        sys.stdout.write(f"log: {run_dir / 'EXECUTION_LOG.txt'}\n")
    return 0 if summary["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
