#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

SURFACE = "IMPERIUM_RESOURCE_FLEET_NODE_PROBE_V0_8_1"


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run(cmd: list[str]) -> dict:
    try:
        out = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=12)
        return {"found": out.returncode == 0, "cmd": cmd, "returncode": out.returncode, "stdout": out.stdout.strip()[:2000], "stderr": out.stderr.strip()[:1000]}
    except Exception as exc:
        return {"found": False, "cmd": cmd, "error": repr(exc)}


def which(name: str) -> str:
    return shutil.which(name) or ""


def repo_root(path: str) -> Path:
    p = Path(path).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "ORGANS").exists():
            return candidate
    return p


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo = repo_root(args.repo_root)
    tools = {
        "python": {"path": sys.executable, "version": sys.version.split()[0]},
        "git": {"path": which("git"), "version": run(["git", "--version"])},
        "node": {"path": which("node"), "version": run(["node", "--version"]) if which("node") else {"found": False}},
        "npm": {"path": which("npm"), "version": run(["npm", "--version"]) if which("npm") else {"found": False}},
    }
    missing = [name for name, data in tools.items() if not data.get("path") and name != "python"]
    local_handoff = Path(os.environ.get("IMPERIUM_LOCAL_HANDOFF") or ((Path(repo.anchor) / "IMPERIUM_LOCAL_HANDOFF") if os.name == "nt" else (repo.parent / "IMPERIUM_LOCAL_HANDOFF"))).resolve()
    payload = {
        "status": "PASS_WITH_WARNINGS" if missing else "PASS",
        "surface": SURFACE,
        "generated_at_utc": now_utc(),
        "node_name": platform.node(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "repo_root": str(repo),
        "local_handoff": str(local_handoff),
        "tools": tools,
        "missing": missing,
        "resource_fleet_note": "Portable Imperium nodes should run this probe before joining shared workload routing.",
        "next_install_hint": "Install missing git/node/npm/python packages, then rerun probe. Ubuntu bootstrap will be formalized in a later Servitor taskpack.",
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
