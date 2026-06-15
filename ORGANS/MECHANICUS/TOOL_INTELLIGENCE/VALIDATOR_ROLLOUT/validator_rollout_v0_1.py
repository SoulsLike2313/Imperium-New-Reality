#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imperium.rollout_ledger.v0_1 - validator_rollout v0_1

For every tool passport found in the repo, runs each declared validator
with a per-validator hard timeout and Windows process-tree kill, then
writes a rollout ledger conforming to imperium.rollout_ledger.v0_1.

Owner-gated: true. Exec mode: static (only runs declared validators).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAS_RICH = True
except Exception:
    HAS_RICH = False

PER_VALIDATOR_TIMEOUT_DEFAULT = 10.0
IS_WIN = os.name == "nt"
PASSPORT_GLOB_RE = re.compile(r"^.+_tool_passport_v[0-9_]+\.json$")


def _kill_tree(pid: int) -> None:
    if IS_WIN:
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True, timeout=3,
            )
        except Exception:
            pass
    else:
        try:
            os.killpg(os.getpgid(pid), 9)
        except Exception:
            pass


def _run(cmd_str: str, cwd: Path, timeout: float) -> Tuple[int, str, str, bool, int]:
    """Returns (exit_code, stdout_tail, stderr_tail, timed_out, elapsed_ms)."""
    creationflags = 0x00000200 if IS_WIN else 0  # CREATE_NEW_PROCESS_GROUP on Windows
    t0 = time.monotonic()
    if IS_WIN:
        p = subprocess.Popen(
            ["cmd.exe", "/d", "/c", cmd_str],
            cwd=str(cwd),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
        )
    else:
        p = subprocess.Popen(
            ["/bin/sh", "-c", cmd_str],
            cwd=str(cwd),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            preexec_fn=os.setsid,
        )
    timed_out = False
    try:
        out, err = p.communicate(timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        _kill_tree(p.pid)
        try:
            out, err = p.communicate(timeout=2)
        except Exception:
            out, err = b"", b""
        rc = -1
        timed_out = True
    dt_ms = int((time.monotonic() - t0) * 1000)

    def tail(b: bytes, n: int = 400) -> str:
        s = (b or b"").decode("utf-8", errors="replace").strip()
        return s if len(s) <= n else s[-n:]

    return rc, tail(out), tail(err), timed_out, dt_ms


def find_passports(repo_root: Path) -> List[Path]:
    organs = repo_root / "ORGANS"
    if not organs.is_dir():
        return []
    results: List[Path] = []
    for path in organs.rglob("*.json"):
        if PASSPORT_GLOB_RE.match(path.name):
            results.append(path)
    return sorted(results)


def resolve_exec(exec_str: str, repo_root: Path, tool_path: str) -> str:
    return (exec_str
            .replace("{repo}", str(repo_root))
            .replace("{tool_path}", tool_path or ""))


def run_rollout(repo_root: Path, dry_run: bool = False,
                name_filter: Optional[str] = None,
                live_log: bool = True) -> Dict[str, Any]:
    passports = find_passports(repo_root)
    results: List[Dict[str, Any]] = []
    counts = {"passed": 0, "failed": 0, "timed_out": 0,
              "errored": 0, "skipped": 0, "no_validators": 0}
    total_validators = 0

    for ppath in passports:
        rel_pp = str(ppath.relative_to(repo_root)).replace("\\", "/")
        try:
            data = json.loads(ppath.read_text(encoding="utf-8-sig"))
        except Exception as e:
            results.append({
                "tool_id": "?", "passport_path": rel_pp,
                "validator_name": "PARSE", "exec": "",
                "status": "error", "exit_code": None,
                "elapsed_ms": 0,
                "stdout_tail": "", "stderr_tail": f"parse: {e}",
            })
            counts["errored"] += 1
            if live_log:
                print(f"  [error] {rel_pp}: parse: {e}", flush=True)
            continue

        tool_id = data.get("tool_id", "?")
        if name_filter and name_filter not in tool_id:
            continue
        tool_path = data.get("tool_path", "")
        validators = data.get("validators") or []

        if not validators:
            results.append({
                "tool_id": tool_id, "passport_path": rel_pp,
                "validator_name": "\u2014", "exec": "",
                "status": "no_validators", "exit_code": None,
                "elapsed_ms": 0, "stdout_tail": "", "stderr_tail": "",
            })
            counts["no_validators"] += 1
            if live_log:
                print(f"  [skip ] {tool_id}: no validators declared", flush=True)
            continue

        for v in validators:
            total_validators += 1
            vname = v.get("name", "?")
            vexec = resolve_exec(v.get("exec", ""), repo_root, tool_path)
            vtimeout = float(v.get("timeout_seconds", PER_VALIDATOR_TIMEOUT_DEFAULT))

            if dry_run:
                results.append({
                    "tool_id": tool_id, "passport_path": rel_pp,
                    "validator_name": vname, "exec": vexec,
                    "status": "skipped", "exit_code": None,
                    "elapsed_ms": 0,
                    "stdout_tail": "[dry-run]", "stderr_tail": "",
                })
                counts["skipped"] += 1
                if live_log:
                    print(f"  [dry  ] {tool_id} \u00b7 {vname}: {vexec[:90]}", flush=True)
                continue

            if live_log:
                print(f"  [run  ] {tool_id} \u00b7 {vname} ...", flush=True)
            rc, sout, serr, timed_out, dt_ms = _run(vexec, repo_root, vtimeout)
            if timed_out:
                status = "timeout"; counts["timed_out"] += 1; tag = "\u26a0 timeout"
            elif rc == 0:
                status = "pass"; counts["passed"] += 1; tag = "\u2713 pass"
            else:
                status = "fail"; counts["failed"] += 1; tag = "\u2717 fail"
            if live_log:
                print(f"  [{tag:>9s}] {tool_id} \u00b7 {vname}  rc={rc}  ({dt_ms} ms)", flush=True)
            results.append({
                "tool_id": tool_id, "passport_path": rel_pp,
                "validator_name": vname, "exec": vexec,
                "status": status, "exit_code": rc,
                "elapsed_ms": dt_ms,
                "stdout_tail": sout, "stderr_tail": serr,
            })

    return {
        "schema_id":        "imperium.rollout_ledger.v0_1",
        "generated_at":     _dt.datetime.now().astimezone().isoformat(),
        "generator":        "validator_rollout_v0_1.py",
        "repo_root":        str(repo_root),
        "total_passports":  len(passports),
        "total_validators": total_validators,
        "summary":          counts,
        "results":          results,
    }


def render(ledger: Dict[str, Any]) -> None:
    if not HAS_RICH:
        print(json.dumps(ledger["summary"], indent=2))
        return
    c = Console()
    t = Table(title="Imperium \u00b7 Validator Rollout", title_style="bold gold1")
    t.add_column("tool_id", style="bold")
    t.add_column("validator")
    t.add_column("status", justify="center")
    t.add_column("rc", justify="right")
    t.add_column("ms", justify="right")
    t.add_column("exec", overflow="fold")
    for r in ledger["results"]:
        st = r["status"]
        mark = {
            "pass":          "[green]\u2713 pass[/]",
            "fail":          "[red]\u2717 fail[/]",
            "timeout":       "[yellow]\u26a0 timeout[/]",
            "error":         "[red]! error[/]",
            "skipped":       "[dim]\u00b7 skipped[/]",
            "no_validators": "[dim]\u2014 none[/]",
        }.get(st, st)
        rc = r.get("exit_code")
        t.add_row(
            str(r.get("tool_id", "?")),
            str(r.get("validator_name", "?")),
            mark,
            "" if rc is None else str(rc),
            str(r.get("elapsed_ms", "")),
            (r.get("exec") or "")[:100],
        )
    c.print(t)
    s = ledger["summary"]
    clean = (s["failed"] == 0 and s["errored"] == 0 and s["timed_out"] == 0)
    border = "green" if clean else "red"
    c.print(Panel.fit(
        f"[bold]Rollout summary[/]\n"
        f"passed        : {s['passed']}\n"
        f"failed        : {s['failed']}\n"
        f"timed_out     : {s['timed_out']}\n"
        f"errored       : {s['errored']}\n"
        f"skipped       : {s['skipped']}\n"
        f"no_validators : {s['no_validators']}\n"
        f"total passports / validators: {ledger['total_passports']} / {ledger['total_validators']}",
        border_style=border,
    ))


def main() -> int:
    ap = argparse.ArgumentParser(description="Run validator rollout across all passports")
    ap.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    ap.add_argument("--out",  default=None, help="Output ledger JSON path")
    ap.add_argument("--dry-run", action="store_true", help="List validators without running them")
    ap.add_argument("--filter",  default=None, help="Substring filter on tool_id")
    ap.add_argument("--quiet",   action="store_true")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    if not (repo_root / "ORGANS").is_dir():
        print(f"error: ORGANS/ not found at {repo_root}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(f"=== validator_rollout v0_1 \u00b7 repo: {repo_root} \u00b7 dry-run: {args.dry_run} ===", flush=True)

    ledger = run_rollout(
        repo_root,
        dry_run=args.dry_run,
        name_filter=args.filter,
        live_log=not args.quiet,
    )

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.quiet:
        print("", flush=True)
        render(ledger)
        if args.out:
            print(f"\nledger: {args.out}")

    s = ledger["summary"]
    return 0 if (s["failed"] == 0 and s["errored"] == 0 and s["timed_out"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
