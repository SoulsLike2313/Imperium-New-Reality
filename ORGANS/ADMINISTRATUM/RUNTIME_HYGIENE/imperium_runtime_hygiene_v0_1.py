#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import time
from pathlib import Path

SURFACE = "IMPERIUM_RUNTIME_HYGIENE_V0_8_1"
DEFAULT_TTL_DAYS = 3


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def repo_root(path: str) -> Path:
    p = Path(path).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "ORGANS").exists():
            return candidate
    return p


def local_handoff_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_LOCAL_HANDOFF")
    if configured:
        return Path(configured).resolve()
    if os.name == "nt":
        return (Path(repo.anchor) / "IMPERIUM_LOCAL_HANDOFF").resolve()
    return (repo.parent / "IMPERIUM_LOCAL_HANDOFF").resolve()


def warp_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_WARP_ROOT")
    if configured:
        return Path(configured).resolve()
    if os.name == "nt":
        return (Path(repo.anchor) / "IMPERIUM_WARPS").resolve()
    return (repo.parent / "IMPERIUM_WARPS").resolve()


def runtime_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_WARP_RUNTIME_ROOT")
    if configured:
        return Path(configured).resolve()
    return local_handoff_root(repo) / "WARP_RUNS"


def safe_relative(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def load_active(repo: Path) -> dict:
    registry = read_json(runtime_root(repo) / "_registry" / "warp_registry.json", {})
    active = read_json(runtime_root(repo) / "_registry" / "active_task.json", {})
    return {"registry": registry, "active_task": active}


def aliases(repo: Path) -> dict:
    handoff = local_handoff_root(repo)
    rr = runtime_root(repo)
    data = load_active(repo)
    registry = data["registry"]
    return {
        "MAIN_REPO": str(Path(str(repo)[:-2]).resolve()) if str(repo).endswith("_H") else str(repo),
        "H_CONTOUR": str(repo) if str(repo).endswith("_H") else str(Path(str(repo) + "_H")),
        "WARP_ROOT": str(warp_root(repo)),
        "LOCAL_HANDOFF": str(handoff),
        "TASK_FORMS": str(handoff / "TASK_FORMS"),
        "WARP_RUNS": str(rr),
        "SERVITOR_OUTPUTS": str(handoff / "SERVITOR_OUTPUTS"),
        "REPORT_BUNDLES": str(handoff / "REPORT_BUNDLES"),
        "RESOURCE_FLEET": str(handoff / "RESOURCE_FLEET"),
        "ACTIVE_WARP": registry.get("path", ""),
        "ACTIVE_RUN": str(rr / registry["warp_id"]) if registry.get("warp_id") else "",
    }


def protected_paths(repo: Path) -> set[str]:
    a = aliases(repo)
    paths = {str(repo.resolve()), str((runtime_root(repo) / "_registry").resolve())}
    for key in ["ACTIVE_WARP", "ACTIVE_RUN"]:
        value = a.get(key)
        if value:
            paths.add(str(Path(value).resolve()))
    return paths


def is_protected(path: Path, protected: set[str]) -> bool:
    resolved = str(path.resolve())
    for item in protected:
        p = Path(item)
        if resolved == str(p.resolve()) or safe_relative(path, p):
            return True
    return False


def candidate_roots(repo: Path) -> list[Path]:
    handoff = local_handoff_root(repo)
    roots = [handoff / "TASK_FORMS", handoff / "SERVITOR_OUTPUTS", handoff / "REPORT_BUNDLES", runtime_root(repo), warp_root(repo)]
    return [root for root in roots if root.exists()]


def scan(repo: Path, ttl_days: int = DEFAULT_TTL_DAYS) -> dict:
    cutoff = time.time() - ttl_days * 86400
    protected = protected_paths(repo)
    candidates = []
    roots = candidate_roots(repo)
    for root in roots:
        for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if child.name == "_registry" or is_protected(child, protected):
                continue
            try:
                mtime = child.stat().st_mtime
            except OSError:
                continue
            age_days = round((time.time() - mtime) / 86400, 2)
            volatile = child.is_dir() or child.suffix.lower() in {".zip", ".json", ".log", ".txt", ".png", ".webm"}
            expired = mtime < cutoff
            candidates.append({
                "path": str(child),
                "root": str(root),
                "age_days": age_days,
                "expired": expired,
                "volatile": volatile,
                "action": "DELETE_CANDIDATE" if expired and volatile else "KEEP_UNTIL_TTL",
            })
    return {
        "status": "PASS",
        "surface": SURFACE,
        "generated_at_utc": now_utc(),
        "host": platform.node(),
        "ttl_days": ttl_days,
        "aliases": aliases(repo),
        "protected_paths": sorted(protected),
        "roots_scanned": [str(root) for root in roots],
        "candidate_count": len(candidates),
        "delete_candidate_count": sum(1 for item in candidates if item["action"] == "DELETE_CANDIDATE"),
        "candidates": candidates[:200],
        "web_policy": "scan only; prune requires CLI --apply",
    }


def prune(repo: Path, ttl_days: int, apply: bool) -> dict:
    report = scan(repo, ttl_days)
    deleted = []
    blocked = []
    for item in report["candidates"]:
        if item.get("action") != "DELETE_CANDIDATE":
            continue
        path = Path(item["path"])
        if not apply:
            continue
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            deleted.append(str(path))
        except Exception as exc:
            blocked.append({"path": str(path), "error": repr(exc)})
    report.update({"mode": "APPLY" if apply else "DRY_RUN", "deleted": deleted, "blocked": blocked})
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("cmd", nargs="?", default="scan", choices=["scan", "prune", "paths", "policy"])
    parser.add_argument("--ttl-days", type=int, default=DEFAULT_TTL_DAYS)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    repo = repo_root(args.repo_root)
    if args.cmd == "paths":
        payload = {"status": "PASS", "surface": SURFACE, "aliases": aliases(repo)}
    elif args.cmd == "policy":
        policy_path = Path(__file__).resolve().with_name("runtime_paths_policy.json")
        payload = read_json(policy_path, {"status": "MISSING", "path": str(policy_path)})
    elif args.cmd == "prune":
        payload = prune(repo, args.ttl_days, args.apply)
    else:
        payload = scan(repo, args.ttl_days)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
