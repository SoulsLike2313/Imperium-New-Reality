#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imperium.toolchain_inventory.v0_1 - toolchain probe v0_3
  * per-tool timing, live progress (python -u)
  * hard 5s timeout per tool with Windows process-tree kill (taskkill /F /T)
  * dropped corepack-yarn shim (causes registry-download hang)
  * dropped duplicate "tauri (npm)" and optional "code" probes
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import platform
import shutil
import subprocess
import sys
import time

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except Exception:
    sys.stderr.write("rich not installed: pip install rich\n")
    sys.exit(2)

PER_CALL_TIMEOUT = 5.0
IS_WIN = os.name == "nt"


def _log(msg: str) -> None:
    print(msg, flush=True)


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


def _run_with_kill(args: list, timeout: float) -> tuple:
    """Returns (returncode, stdout_bytes, stderr_bytes, timed_out)."""
    creationflags = 0
    if IS_WIN:
        # CREATE_NEW_PROCESS_GROUP so we own the process tree
        creationflags = 0x00000200  # CREATE_NEW_PROCESS_GROUP
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creationflags,
    )
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err, False
    except subprocess.TimeoutExpired:
        _kill_tree(p.pid)
        try:
            out, err = p.communicate(timeout=2)
        except Exception:
            out, err = b"", b""
        return -1, out, err, True


def run(cmd: str, args: tuple = ()) -> dict:
    t0 = time.monotonic()
    exe = shutil.which(cmd)
    if not exe:
        dt = time.monotonic() - t0
        _log(f"  * {cmd:<22s} not found            ({dt*1000:6.0f} ms)")
        return {"present": False, "path": None, "version": None, "raw": None, "elapsed_ms": int(dt * 1000)}
    try:
        rc, stdout, stderr, timed_out = _run_with_kill([exe, *args], PER_CALL_TIMEOUT)
        dt = time.monotonic() - t0
        if timed_out:
            _log(f"  * {cmd:<22s} ! TIMEOUT >{PER_CALL_TIMEOUT}s   ({dt*1000:6.0f} ms)")
            return {"present": True, "path": exe, "version": "TIMEOUT", "raw": f"timeout >{PER_CALL_TIMEOUT}s; killed tree", "elapsed_ms": int(dt * 1000)}
        out = (stdout or b"").decode("utf-8", errors="replace").strip()
        err = (stderr or b"").decode("utf-8", errors="replace").strip()
        text = out or err
        first = text.splitlines()[0] if text else ""
        _log(f"  * {cmd:<22s} ok  {first[:48]:<48s} ({dt*1000:6.0f} ms)")
        return {"present": True, "path": exe, "version": first, "raw": text, "elapsed_ms": int(dt * 1000)}
    except Exception as e:
        dt = time.monotonic() - t0
        _log(f"  * {cmd:<22s} X ERR {str(e)[:40]:<40s} ({dt*1000:6.0f} ms)")
        return {"present": True, "path": exe, "version": "ERR", "raw": str(e), "elapsed_ms": int(dt * 1000)}


def win_webview2() -> dict:
    t0 = time.monotonic()
    for base in (
        r"C:\Program Files (x86)\Microsoft\EdgeWebView\Application",
        r"C:\Program Files\Microsoft\EdgeWebView\Application",
    ):
        if os.path.isdir(base):
            try:
                vers = sorted([d for d in os.listdir(base) if d and d[0].isdigit()])
                if vers:
                    dt = time.monotonic() - t0
                    _log(f"  * WebView2 runtime       ok  {vers[-1]:<48s} ({dt*1000:6.0f} ms)")
                    return {"present": True, "path": os.path.join(base, vers[-1]), "version": vers[-1], "raw": "", "elapsed_ms": int(dt * 1000)}
            except Exception:
                pass
    dt = time.monotonic() - t0
    _log(f"  * WebView2 runtime       not found            ({dt*1000:6.0f} ms)")
    return {"present": False, "path": None, "version": None, "raw": "EdgeWebView folder not found", "elapsed_ms": int(dt * 1000)}


def win_vs_buildtools() -> dict:
    t0 = time.monotonic()
    vswhere = r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    if not os.path.isfile(vswhere):
        dt = time.monotonic() - t0
        _log(f"  * MSVC Build Tools       not found (no vswhere)  ({dt*1000:6.0f} ms)")
        return {"present": False, "path": None, "version": None, "raw": "vswhere.exe not found", "elapsed_ms": int(dt * 1000)}
    try:
        rc, stdout, stderr, timed_out = _run_with_kill(
            [vswhere, "-products", "*", "-requires", "Microsoft.VisualStudio.Workload.VCTools", "-format", "json"],
            PER_CALL_TIMEOUT,
        )
        dt = time.monotonic() - t0
        if timed_out:
            _log(f"  * MSVC Build Tools       ! TIMEOUT >{PER_CALL_TIMEOUT}s   ({dt*1000:6.0f} ms)")
            return {"present": True, "path": vswhere, "version": "TIMEOUT", "raw": "timeout; killed tree", "elapsed_ms": int(dt * 1000)}
        out = (stdout or b"").decode("utf-8", errors="replace").strip()
        if out.startswith("["):
            data = json.loads(out)
            if data:
                p = data[0]
                _log(f"  * MSVC Build Tools       ok  {p.get('installationVersion',''):<48s} ({dt*1000:6.0f} ms)")
                return {"present": True, "path": p.get("installationPath"), "version": p.get("installationVersion"), "raw": p.get("displayName"), "elapsed_ms": int(dt * 1000)}
        _log(f"  * MSVC Build Tools       not detected (VCTools missing) ({dt*1000:6.0f} ms)")
        return {"present": False, "path": None, "version": None, "raw": "VCTools workload not detected", "elapsed_ms": int(dt * 1000)}
    except Exception as e:
        dt = time.monotonic() - t0
        _log(f"  * MSVC Build Tools       X ERR {str(e)[:40]:<40s} ({dt*1000:6.0f} ms)")
        return {"present": False, "path": None, "version": None, "raw": str(e), "elapsed_ms": int(dt * 1000)}


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("usage: python toolchain_probe_v0_3.py <out_json_path>\n")
        return 2
    out_path = sys.argv[1]

    total_t0 = time.monotonic()
    _log("=== toolchain probe v0_3 (5s hard timeout, process-tree kill) ===")
    _log(f"host: {platform.node()} | os: {platform.platform()} | arch: {platform.machine()}")
    _log("")

    components: list[dict] = []

    def add(cat: str, tool: str, info: dict, notes: str = "") -> None:
        components.append({"category": cat, "tool": tool, **info, "notes": notes})

    _log("[rust]")
    add("rust", "rustup",      run("rustup", ("--version",)))
    add("rust", "rustc",       run("rustc",  ("--version",)))
    add("rust", "cargo",       run("cargo",  ("--version",)))
    add("rust", "cargo-tauri", run("cargo",  ("tauri", "--version")), "Tauri 2.x CLI as cargo subcommand")

    _log("")
    _log("[node]")
    add("node", "node",         run("node", ("--version",)))
    add("node", "npm",          run("npm",  ("--version",)))
    add("node", "pnpm",         run("pnpm", ("--version",)))
    # NOTE: yarn dropped - corepack shim hangs on registry download; not in our stack.
    # NOTE: tauri (npm) dropped - duplicate of cargo-tauri.

    _log("")
    _log("[build]")
    add("build", "WebView2 runtime",     win_webview2(),     "Tauri 2.x req on Windows")
    add("build", "MSVC C++ Build Tools", win_vs_buildtools(), "Tauri 2.x req on Windows for native linking")

    _log("")
    _log("[misc]")
    add("misc", "python", run("python", ("--version",)))
    add("misc", "git",    run("git",    ("--version",)))
    # NOTE: VS Code dropped - code.CMD can hang via Node spawn; not in readiness gate.

    total_dt = time.monotonic() - total_t0
    _log("")
    _log(f"total elapsed: {total_dt*1000:.0f} ms")
    _log("")

    req = ["rustup", "rustc", "cargo", "node", "WebView2 runtime", "MSVC C++ Build Tools"]
    missing = [c["tool"] for c in components if c["tool"] in req and not c["present"]]
    present = [c["tool"] for c in components if c["tool"] in req and c["present"]]
    ready = len(missing) == 0

    payload = {
        "schema_id": "imperium.toolchain_inventory.v0_1",
        "probe_version": "v0_3",
        "host": {"hostname": platform.node(), "os": platform.platform(), "arch": platform.machine()},
        "captured_at": _dt.datetime.now().astimezone().isoformat(),
        "components": components,
        "required_for_tauri": {"missing": missing, "present": present, "ready": ready},
        "total_elapsed_ms": int(total_dt * 1000),
        "dropped_from_probe": [
            {"tool": "yarn",        "reason": "corepack shim hangs on registry download; not in stack"},
            {"tool": "tauri (npm)", "reason": "duplicate of cargo-tauri"},
            {"tool": "code",        "reason": "code.CMD can hang via Node spawn; not in readiness gate"},
        ],
    }

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    c = Console()
    for cat in ("rust", "node", "build", "misc"):
        t = Table(title=f"Toolchain \u00b7 {cat}", show_lines=False, title_style="bold gold1")
        t.add_column("tool", style="bold")
        t.add_column("present")
        t.add_column("version")
        t.add_column("ms", justify="right")
        t.add_column("path / notes", overflow="fold")
        for c_ in components:
            if c_["category"] != cat:
                continue
            if not c_["present"]:
                ok = "[red]\u2717[/]"
            elif c_.get("version") == "TIMEOUT":
                ok = "[yellow]\u26a0[/]"
            elif c_.get("version") == "ERR":
                ok = "[red]![/]"
            else:
                ok = "[green]\u2713[/]"
            ver = c_.get("version") or ""
            ms = str(c_.get("elapsed_ms", ""))
            path = c_.get("path") or c_.get("notes") or c_.get("raw") or ""
            t.add_row(c_["tool"], ok, str(ver), ms, str(path))
        c.print(t)

    if ready:
        border = "green"
        miss_str = "\u2014 none \u2014"
    else:
        border = "yellow"
        miss_str = ", ".join(missing)
    panel_text = (
        f"[bold]Tauri 2.x readiness[/]\n"
        f"missing required: {miss_str}\n"
        f"total elapsed: {int(total_dt*1000)} ms\n"
        f"receipt: {out_path}"
    )
    c.print(Panel.fit(panel_text, border_style=border))
    return 0


if __name__ == "__main__":
    sys.exit(main())
