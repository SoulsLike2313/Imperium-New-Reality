#!/usr/bin/env python3
"""inquisition.py -- Inquisition organ front-tool.

Subcommands:
  --health                       JSON status of all 10 inq_*.py tools (Q25)
  hook <H1..H6> --pack-dir <d>   Run the canonical hook bundle for the stage
  dispatch --tool <name> ...      Direct dispatch to a single inq_<name>.py
  tui                             Launch rich-based TUI (6 tabs, Q22) -- best-effort

Hook bundles (charter):
  H1_POST_ADMIT       : inq_secrets, inq_pi_scan, inq_anomaly
  H2_PRE_PERMIT       : inq_trust, inq_ban
  H3_WARP_TEST        : (no-op in v0_1; reserved for warp-test extension)
  H4_PRE_APPLY        : inq_secrets, inq_redact (dry-run)
  H5_POST_LAND        : inq_audit (verify-chain), inq_trace (status)
  H6_ON_DEMAND        : (per --tool only)

Return semantics:
  exit code 0 if all sub-tools returned 0/OK/HINT/NOOP
  exit code 1 if any sub-tool returned BLOCK_* (worst-of)
  exit code 2 if any sub-tool FAIL_CLOSED

Each hook invocation emits an aggregated verdict JSON on stdout (Q19).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_FAIL_CLOSED, EXIT_BLOCK, EXIT_OK
from inq_patterns import load_thresholds

ALL_TOOLS = [
    "inq_report",
    "inq_patterns",
    "inq_secrets",
    "inq_pi_scan",
    "inq_redact",
    "inq_anomaly",
    "inq_trust",
    "inq_ban",
    "inq_audit",
    "inq_trace",
]

HOOK_BUNDLES: Dict[str, List[str]] = {
    "H1_POST_ADMIT": ["inq_secrets", "inq_pi_scan", "inq_anomaly"],
    "H2_PRE_PERMIT": ["inq_trust", "inq_ban"],
    "H3_WARP_TEST": [],
    "H4_PRE_APPLY": ["inq_secrets", "inq_redact"],
    "H5_POST_LAND": ["inq_audit", "inq_trace"],
    "H6_ON_DEMAND": [],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tools_dir() -> Path:
    return HERE


def _tool_path(name: str) -> Path:
    return _tools_dir() / f"{name}.py"


def _ensure_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def cmd_health(args: argparse.Namespace) -> int:
    """Q25: granular health JSON listing all 10 tools and per-tool status."""
    out: Dict[str, Any] = {
        "schema_version": "inq.health.v0_1",
        "timestamp_utc": _utc_now(),
        "tools": [],
        "overall": "OK",
    }
    overall_ok = True
    for name in ALL_TOOLS:
        tp = _tool_path(name)
        entry: Dict[str, Any] = {
            "name": name,
            "path": str(tp),
            "present": tp.is_file(),
        }
        if tp.is_file():
            try:
                bytes_ = tp.read_bytes()
                import hashlib
                entry["sha256"] = hashlib.sha256(bytes_).hexdigest()
                entry["size_bytes"] = len(bytes_)
                # quick syntax check via py_compile in-process
                try:
                    compile(bytes_.decode("utf-8"), str(tp), "exec")
                    entry["syntax_ok"] = True
                    entry["status"] = "OK"
                except SyntaxError as e:
                    entry["syntax_ok"] = False
                    entry["status"] = "SYNTAX_ERROR"
                    entry["error"] = f"{type(e).__name__}: {e.msg} at line {e.lineno}"
                    overall_ok = False
            except Exception as e:
                entry["status"] = "READ_ERROR"
                entry["error"] = f"{type(e).__name__}: {e}"
                overall_ok = False
        else:
            entry["status"] = "MISSING"
            overall_ok = False
        out["tools"].append(entry)

    # Validate configs
    try:
        thresholds = load_thresholds(
            Path(args.config_dir).resolve() if args.config_dir else None
        )
        out["configs"] = {
            "signatures": "OK",
            "redaction": "OK",
            "thresholds": "OK",
            "threshold_count": len(thresholds.get("thresholds", {})),
        }
    except Exception as e:
        out["configs"] = {"error": f"{type(e).__name__}: {e}"}
        overall_ok = False

    out["overall"] = "OK" if overall_ok else "DEGRADED"
    sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2 if args.pretty else None) + "\n")
    return 0 if overall_ok else 1


def _run_tool(
    name: str,
    *,
    pack_dir: Path,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    extra: Optional[List[str]] = None,
    timeout: int = 30,
) -> Tuple[Dict[str, Any], int]:
    tp = _tool_path(name)
    if not tp.is_file():
        return ({
            "verdict": "FAIL_CLOSED",
            "tool": name,
            "reasons": [f"tool missing: {tp}"],
            "exit_code": EXIT_FAIL_CLOSED,
        }, EXIT_FAIL_CLOSED)
    cmd = [
        sys.executable, str(tp),
        "--pack-dir", str(pack_dir),
        "--task-id", task_id,
        "--author", author,
        "--stage", stage,
        "--reports-dir", reports_dir,
    ]
    if extra:
        cmd.extend(extra)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ({
            "verdict": "FAIL_CLOSED",
            "tool": name,
            "reasons": [f"timeout after {timeout}s"],
            "exit_code": 3,
        }, 3)
    except Exception as e:
        return ({
            "verdict": "FAIL_CLOSED",
            "tool": name,
            "reasons": [f"subprocess_error: {type(e).__name__}: {e}"],
            "exit_code": EXIT_FAIL_CLOSED,
        }, EXIT_FAIL_CLOSED)
    # Parse last non-empty stdout line as JSON verdict
    verdict: Dict[str, Any] = {}
    for line in reversed(proc.stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            verdict = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    if not verdict:
        verdict = {
            "verdict": "FAIL_CLOSED",
            "tool": name,
            "reasons": [f"no JSON verdict on stdout (rc={proc.returncode})"],
            "exit_code": EXIT_FAIL_CLOSED,
        }
    verdict.setdefault("_subprocess_rc", proc.returncode)
    return verdict, int(verdict.get("exit_code", proc.returncode))


def cmd_hook(args: argparse.Namespace) -> int:
    """Run a canonical hook bundle, aggregate verdicts."""
    stage = args.hook_stage
    if stage not in HOOK_BUNDLES:
        sys.stdout.write(json.dumps({
            "verdict": "FAIL_CLOSED",
            "reasons": [f"unknown hook stage: {stage}"],
            "exit_code": 4,
        }) + "\n")
        return 4
    tools = HOOK_BUNDLES[stage]
    if not tools:
        sys.stdout.write(json.dumps({
            "schema_version": "inq.verdict.v0_1",
            "verdict": "NOOP",
            "stage": stage,
            "reasons": [f"hook {stage} has no bundle in v0_1"],
            "tool": "inquisition",
            "task_id": args.task_id,
            "author": args.author,
            "issued_utc": _utc_now(),
            "exit_code": 0,
            "sub_verdicts": [],
        }, ensure_ascii=False) + "\n")
        return 0
    pack_dir = Path(args.pack_dir).resolve()
    sub_verdicts: List[Dict[str, Any]] = []
    worst = 0
    overall_verdict = "OK"
    block_reasons: List[str] = []
    fail_reasons: List[str] = []
    hint_reasons: List[str] = []
    extra_per_tool = {
        "inq_redact": [],  # dry-run by default in PRE-ADMIT/PRE-APPLY
    }
    if args.force_inq:
        extra_per_tool["inq_secrets"] = ["--force-inq"]
        extra_per_tool["inq_pi_scan"] = ["--force-inq"]
    start = time.time()
    for name in tools:
        verdict, rc = _run_tool(
            name,
            pack_dir=pack_dir,
            task_id=args.task_id,
            author=args.author,
            stage=stage,
            reports_dir=args.reports_dir,
            extra=extra_per_tool.get(name, []),
            timeout=args.timeout,
        )
        sub_verdicts.append(verdict)
        v = verdict.get("verdict", "UNKNOWN")
        if rc > worst:
            worst = rc
        if v.startswith("BLOCK_"):
            block_reasons.append(f"{name}: {v}")
        elif v == "FAIL_CLOSED":
            fail_reasons.append(f"{name}: {v}")
        elif v.startswith("HINT_"):
            hint_reasons.append(f"{name}: {v}")
    elapsed = time.time() - start

    if fail_reasons:
        overall_verdict = "FAIL_CLOSED"
    elif block_reasons:
        overall_verdict = "BLOCK_HOOK"
    elif hint_reasons:
        overall_verdict = "HINT_HOOK"
    else:
        overall_verdict = "OK"

    reasons: List[str] = []
    if fail_reasons:
        reasons.extend(fail_reasons)
    if block_reasons:
        reasons.extend(block_reasons)
    if hint_reasons:
        reasons.extend(hint_reasons)
    if not reasons:
        reasons.append(f"all {len(tools)} hook tools passed")

    agg = {
        "schema_version": "inq.verdict.v0_1",
        "verdict": overall_verdict,
        "stage": stage,
        "reasons": reasons,
        "tool": "inquisition",
        "task_id": args.task_id,
        "author": args.author,
        "issued_utc": _utc_now(),
        "exit_code": worst,
        "elapsed_sec": round(elapsed, 3),
        "sub_verdicts": sub_verdicts,
    }
    sys.stdout.write(json.dumps(agg, ensure_ascii=False) + "\n")
    return worst


def cmd_dispatch(args: argparse.Namespace) -> int:
    """Run a single tool with the given extra args."""
    name = args.tool
    if name not in ALL_TOOLS:
        sys.stdout.write(json.dumps({
            "verdict": "FAIL_CLOSED",
            "reasons": [f"unknown tool: {name}"],
            "exit_code": 4,
        }) + "\n")
        return 4
    extra = args.tool_args or []
    verdict, rc = _run_tool(
        name,
        pack_dir=Path(args.pack_dir).resolve(),
        task_id=args.task_id,
        author=args.author,
        stage=args.stage,
        reports_dir=args.reports_dir,
        extra=extra,
        timeout=args.timeout,
    )
    sys.stdout.write(json.dumps(verdict, ensure_ascii=False) + "\n")
    return rc


def cmd_tui(args: argparse.Namespace) -> int:
    """Best-effort TUI. Tries to import 'rich'; falls back to plain text."""
    try:
        from rich.console import Console  # type: ignore
        from rich.table import Table  # type: ignore
        from rich.panel import Panel  # type: ignore
    except ImportError:
        return _tui_plain(args)
    return _tui_rich(args)


def _tui_plain(args: argparse.Namespace) -> int:
    print("")
    print("=" * 72)
    print("INQUISITION TUI (plain mode - 'rich' not installed)")
    print("=" * 72)
    print("")
    print("Tabs (Q22):")
    print("  [1] REPORTS    - browse _INQUISITION/REPORTS/YYYY-MM-DD/<task>/")
    print("  [2] SIGNATURES - view SIGNATURES.json patterns + counts")
    print("  [3] TRUST      - view authors.json scores / probation")
    print("  [4] BAN_LIST   - view bans.jsonl events")
    print("  [5] PURGE      - PURGE_PROTOCOL status (DORMANT unless core_ready)")
    print("  [6] EVENTS     - audit chain timeline")
    print("  [X] exit")
    print("")
    print("Action:")
    print("  [Q] Quick: pack generator stub (read-only; v0_1 placeholder)")
    print("")
    print("This is a plain-text fallback. Install 'rich' for interactive TUI.")
    print("To check live state programmatically, use:")
    print("  python3 inquisition.py --health")
    print("")
    return 0


def _tui_rich(args: argparse.Namespace) -> int:
    from rich.console import Console  # type: ignore
    from rich.table import Table  # type: ignore
    from rich.panel import Panel  # type: ignore
    console = Console()
    console.rule("[bold red]INQUISITION TUI v0_1")

    # tools status
    table = Table(title="Tools (10)", show_lines=False)
    table.add_column("#", justify="right")
    table.add_column("Tool")
    table.add_column("Present")
    table.add_column("Status")
    for i, name in enumerate(ALL_TOOLS, 1):
        tp = _tool_path(name)
        present = "[green]yes" if tp.is_file() else "[red]no"
        status = "OK" if tp.is_file() else "MISSING"
        table.add_row(str(i), name, present, status)
    console.print(table)

    # configs
    try:
        thresholds = load_thresholds(
            Path(args.config_dir).resolve() if args.config_dir else None
        )
        n = len(thresholds.get("thresholds", {}))
        console.print(Panel(f"Configs OK -- {n} thresholds loaded", title="Configs"))
    except Exception as e:
        console.print(Panel(f"[red]Configs ERROR: {e}", title="Configs"))

    console.print(
        Panel(
            "Tabs: [1] REPORTS  [2] SIGNATURES  [3] TRUST  [4] BAN_LIST  "
            "[5] PURGE  [6] EVENTS    Action: [Q] Quick   [X] exit",
            title="Navigation (read-only TUI per Q23)",
        )
    )
    console.print(
        "[yellow]TUI v0_1 is read-only. All edits go through pack -> gate -> audit (Q23).[/yellow]"
    )
    return 0


def main() -> int:
    _ensure_utf8()
    ap = argparse.ArgumentParser(prog="inquisition")
    ap.add_argument("--health", action="store_true", help="Emit JSON health report and exit")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--config-dir", default=None)
    sub = ap.add_subparsers(dest="cmd")

    p_hook = sub.add_parser("hook")
    p_hook.add_argument("hook_stage")
    p_hook.add_argument("--pack-dir", required=True)
    p_hook.add_argument("--task-id", required=True)
    p_hook.add_argument("--author", required=True)
    p_hook.add_argument("--reports-dir", default="ORGANS/INQUISITION/REPORTS")
    p_hook.add_argument("--force-inq", action="store_true")
    p_hook.add_argument("--timeout", type=int, default=30)

    p_disp = sub.add_parser("dispatch")
    p_disp.add_argument("--tool", required=True)
    p_disp.add_argument("--pack-dir", required=True)
    p_disp.add_argument("--task-id", required=True)
    p_disp.add_argument("--author", required=True)
    p_disp.add_argument("--stage", required=True)
    p_disp.add_argument("--reports-dir", default="ORGANS/INQUISITION/REPORTS")
    p_disp.add_argument("--timeout", type=int, default=30)
    p_disp.add_argument("--tool-args", nargs=argparse.REMAINDER, default=[])

    sub.add_parser("tui")

    args = ap.parse_args()
    if args.health:
        return cmd_health(args)
    if args.cmd == "hook":
        return cmd_hook(args)
    if args.cmd == "dispatch":
        return cmd_dispatch(args)
    if args.cmd == "tui":
        return cmd_tui(args)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
